import argparse
import datetime
import random
import re
import time

import pymysql
import requests

from app.ai.utils.MySqlUtil import GetMysqlCon

TOPICS = {
    "Java":       ("review-java", 100),        # 正好 100 题
    "前端":       ("review-frontend", 100),    # 共 464 题
    "C语言":      ("review-c", 100),           # 共 252 题
    "机器学习":   ("review-ml", 100),          # 共 376 题
    "软件测试":   ("review-test", 100),        # 共 393 题
    "算法":       ("nine-chapter", 67),        # 共 67 题，全要
    "计算机网络": ("review-network", 8),       # 共 8 题，全要
}

# 题目类型 —— 表里这个字段是 NOT NULL，这些复习题都属于"技术知识"
QUESTION_TYPE = "技术知识"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36"
    )
}


class SpiderNKW:
    """牛客复习专题爬虫

    limit      每个方向最多抓多少题
    dry_run    True 就只打印、不入库
    """

    def __init__(self, limit=None, min_sleep=1.0, max_sleep=2.5, dry_run=False):
        # limit=None 表示用 TOPICS 里每个方向自己的计划题数；
        # 命令行显式传了 --limit 就用它覆盖所有方向
        self.limit = limit
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        self.dry_run = dry_run
        self.conn = None
        if not dry_run:
            self.conn = GetMysqlCon.get_mysql_con()
            if isinstance(self.conn, str):          # 连接失败时它返回的是错误字符串
                raise RuntimeError(f"数据库连不上: {self.conn}")

    # ---------------- 抓 ----------------
    def fetch_page(self, slug, page):
        """抓某个专题的第 page 题，返回 HTML；失败返回 None"""
        url = f"https://www.nowcoder.com/ta/{slug}/review?page={page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
        except Exception as e:
            print(f"    请求异常 page={page}: {type(e).__name__} {e}")
            return None
        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code} page={page}")
            return None
        resp.encoding = "utf-8"
        return resp.text

    @staticmethod
    def total_pages(html):
        """从分页控件里读出这个专题一共多少页（读不到就返回 None）"""
        nums = [int(p) for p in re.findall(r"page=(\d+)", html) if p.isdigit()]
        return max(nums) if nums else None

    @staticmethod
    def parse(html):
        """从 HTML 里抠出 (题目, 答案)；抠不到返回 (None, None)"""
        # 题目
        title_match = re.findall('<div class="final-question">(.*?)</div>', html, re.S)
        if not title_match:
            return None, None
        title = re.sub(r"</?p>|<div>|</div>", "", title_match[0])
        title = re.sub(r"\s+", " ", title).strip()

        # 答案：从答案块开头截到操作按钮之前
        answer_match = re.findall(
            '<div class="design-answer-box">(.*?)<div class="final-action clearfix">', html, re.S
        )
        if not answer_match:
            return title, ""            # 题目有、答案没抠到，也算抓到
        answer = answer_match[0]
        answer = re.sub(r"</?div>|<br\s*/?>|</?p>|</?span>", "", answer)
        # 压缩多余空行，但保留换行（答案里的代码块需要换行）
        answer = re.sub(r"[ \t]+", " ", answer)
        answer = re.sub(r"\n\s*\n+", "\n", answer).strip()
        return title, answer

    # ---------------- 存 ----------------
    def exists(self, title):
        """按题目判重：已存在就跳过（这也是断点续爬的关键）"""
        if self.conn is None:
            return False
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM question_bank WHERE question_title=%s LIMIT 1", (title,))
            return cur.fetchone() is not None

    def save(self, title, answer, subject):
        """入库。返回 True 表示新插入，False 表示已存在/未入库"""
        if self.dry_run:
            return True
        if self.exists(title):
            return False
        with self.conn.cursor() as cur:
            # 参数化！题目和答案里带单引号也不会把 SQL 弄坏
            cur.execute(
                "INSERT INTO question_bank"
                "(question_title, answer, question_type, question_subject) "
                "VALUES(%s, %s, %s, %s)",
                (title, answer, QUESTION_TYPE, subject),
            )
        self.conn.commit()
        return True

    # ---------------- 一个方向 ----------------
    def crawl_topic(self, subject, slug, plan=None):
        """抓一个方向，返回 (新增, 已存在, 失败)"""
        # 命令行 --limit 优先，否则用这个方向的计划题数
        limit = self.limit or plan or 100
        added = skipped = failed = 0

        print(f"\n{'=' * 60}\n方向: {subject}  (专题 {slug})  计划 {limit} 题\n{'=' * 60}")

        page = 1
        while added + skipped < limit:
            html = self.fetch_page(slug, page)
            if html is None:
                failed += 1
                page += 1
                if failed >= 5:                 # 连续失败就放弃这个方向
                    print("    连续失败过多，跳过这个方向")
                    break
                time.sleep(random.uniform(self.min_sleep, self.max_sleep))
                continue

            if page == 1:
                total = self.total_pages(html)
                if total:
                    print(f"    这个专题一共 {total} 页，实际只会抓 {min(limit, total)} 题")

            title, answer = self.parse(html)
            if not title:
                print(f"    page={page} 没抓到题目，可能是专题到头了，停止")
                break

            if self.save(title, answer, subject):
                added += 1
                print(f"    [{added:>3}/{limit}] {title[:50]}")
            else:
                skipped += 1
                print(f"    (已存在跳过) {title[:50]}")

            page += 1
            time.sleep(random.uniform(self.min_sleep, self.max_sleep))

        print(f"    => {subject}: 新增 {added} 条, 跳过 {skipped} 条, 失败 {failed} 次")
        return added, skipped, failed

    def crawl_all(self, topics=None):
        topics = topics or TOPICS
        total_added = total_skipped = 0
        for subject, (slug, plan) in topics.items():
            added, skipped, failed = self.crawl_topic(subject, slug, plan)
            total_added += added
            total_skipped += skipped
        print(f"\n{'=' * 60}")
        print(f"全部完成：新增 {total_added} 条，跳过（已存在）{total_skipped} 条")
        return total_added

    def close(self):
        if self.conn:
            self.conn.close()

    def stats(self):
        """看下库里各方向现在有多少题"""
        if self.conn is None:
            print("(dry-run 模式，没有连库)")
            return
        with self.conn.cursor() as cur:
            cur.execute("SELECT question_subject, COUNT(*) c FROM question_bank "
                        "GROUP BY question_subject ORDER BY c DESC")
            print("\n库里各方向题数：")
            for row in cur.fetchall():
                print(f"    {row['question_subject']:<12} {row['c']:>5} 条")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只打印不入库")
    parser.add_argument("--topic", help="只抓某个方向，例如 --topic Java")
    parser.add_argument("--limit", type=int, default=None,
                        help="每个方向最多抓多少题（不传就用 TOPICS 里的计划数）")
    args = parser.parse_args()

    spider = SpiderNKW(limit=args.limit, dry_run=args.dry_run)
    try:
        spider.stats()
        topics = {args.topic: TOPICS[args.topic]} if args.topic else TOPICS
        spider.crawl_all(topics)
        spider.stats()
    finally:
        spider.close()
