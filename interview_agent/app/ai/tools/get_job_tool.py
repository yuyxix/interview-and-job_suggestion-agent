import json
import random
import time
from typing import Any, Iterable, Iterator, Optional

import requests
from langchain_core.tools import StructuredTool

from app.ai.tools.schema.get_job_schema import (
    JOB_FIELDS,
    GetJobSchema,
    JobSearchParams,
)

API_URL = "https://fe-api.zhaopin.com/c/i/search/positions"
_V = "0.43240637"
CLIENT_ID = "63ce3555-d2f2-470a-80f4-8538cee76c41"


class GetJobTool:

    # 一、构造：所有可变配置集中在这里
    def __init__(
        self,
        city_code: str = "489",     # 489 = 全国
        page_size: int = 20,        # 每页条数：实测接口每页最多给 20 条，传更大也只返回 20
        max_pages: int = 3,         # 每个关键词默认翻几页
        min_sleep: float = 1,       # 请求间隔下限（秒），别调太小，容易被封
        max_sleep: float = 3,       # 请求间隔上限（秒）
        max_retry: int = 3,         # 单页失败重试次数
        return_limit: int = 30,     # 工具一次最多返回多少条（保护智能体的上下文）
    ):
        self.city_code = city_code
        self.page_size = page_size
        self.max_pages = max_pages
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        self.max_retry = max_retry
        self.return_limit = return_limit
    # 二、静态工具（不依赖实例配置）
    @staticmethod
    def gen_page_request_id() -> str:
        """生成请求 ID：时间戳-随机数，接口要求每次请求都带新的"""
        timestamp = int(time.time() * 1000)
        rand = random.randint(100000, 999999)
        return f"{timestamp}-{rand}"

    @staticmethod
    def traverse_job_tree(job_tree: dict) -> Iterator[tuple]:
        for industry, domain_map in job_tree.items():
            for domain, role_map in domain_map.items():
                for job_role, keywords in role_map.items():
                    for keyword in keywords:
                        yield industry, domain, job_role, keyword

    @staticmethod
    def parse_job(raw: dict, industry: str = "", domain: str = "",
                  job_role: str = "", keyword: str = "") -> dict:
        """把接口返回的一条原始数据整理成统一字段（字段清单见 JOB_FIELDS）"""
        # 技能标签接口给了两处（skillLabel / jobSkillTags），取有值的那份，
        # 拼成字符串，方便后面按字段模糊筛
        tag_source = raw.get("skillLabel") or raw.get("jobSkillTags") or []
        skills = [t.get("name") or t.get("value") or "" for t in tag_source]
        return {
            "job_id":     raw.get("jobId"),
            "industry":   industry,
            "domain":     domain,
            "job_role":   job_role,
            "keyword":    keyword,
            "job_name":   raw.get("name", ""),
            "company":    raw.get("companyName", ""),
            "city":       raw.get("workCity", ""),
            "salary":     raw.get("salary60", ""),
            "experience": raw.get("workingExp", ""),
            "degree":     raw.get("education", ""),
            "job_type":   raw.get("subJobTypeLevelName", ""),   # 岗位类型
            "work_type":  raw.get("workType", ""),              # 全职 / 兼职 / 实习
            "skills":     "，".join(s for s in skills if s),
        }

    @staticmethod
    def filter_jobs(jobs: list[dict], **conditions: Any) -> list[dict]:
        if not conditions:
            return list(jobs)

        def match(job: dict) -> bool:
            for key, cond in conditions.items():
                value = job.get(key, "")
                if callable(cond):
                    if not cond(value):
                        return False
                elif isinstance(cond, (list, tuple, set)):
                    if value not in cond:
                        return False
                else:
                    if cond not in str(value):
                        return False
            return True

        return [job for job in jobs if match(job)]

    @staticmethod
    def select_fields(jobs: list[dict], fields: Iterable[str]) -> list[dict]:
        """只保留指定字段（智能体只关心名字和薪资时，就传这两个）"""
        fields = list(fields)
        return [{k: job.get(k) for k in fields} for job in jobs]

    @staticmethod
    def count_by(jobs: list[dict], field: str) -> dict:
        """按某个字段统计数量，比如 count_by(jobs, 'city') 看各城市岗位数"""
        result: dict = {}
        for job in jobs:
            key = job.get(field, "")
            result[key] = result.get(key, 0) + 1
        return dict(sorted(result.items(), key=lambda kv: kv[1], reverse=True))

    # 三、抓取
    def fetch_jobs(
        self,
        keyword: str,
        page: int = 1,
        retries: int = 0,
        city_code: Optional[str] = None,
    ) -> list[dict]:
        city = city_code or self.city_code

        url = (
            f"{API_URL}?_v={_V}"
            f"&x-zp-page-request-id={self.gen_page_request_id()}"
            f"&x-zp-client-id={CLIENT_ID}"
        )

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.zhaopin.com",
            "Referer": "https://www.zhaopin.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
            ),
            "x-zp-page-code": "4019",
            "x-zp-platform": "13",
            "x-zp-business-system": "1",
        }

        payload = {
            "S_SOU_FULL_INDEX": keyword,
            "S_SOU_WORK_CITY": city,
            "order": 4,
            "pageIndex": page,
            "pageSize": self.page_size,
            "anonymous": 1,
            "eventScenario": "pcSearchedSouSearch",
            "platform": 13,
            "version": "0.0.0",
        }

        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}")
            data = resp.json()
            return data.get("data", {}).get("list", [])
        except Exception as e:
            if retries < self.max_retry:
                print(f"请求失败，第 {page} 页重试 {retries + 1}/{self.max_retry} | 错误: {e}")
                time.sleep(random.uniform(self.min_sleep, self.max_sleep))
                return self.fetch_jobs(keyword, page, retries + 1, city)
            print(f"请求失败，第 {page} 页已达最大重试次数")
            return []

    def iter_jobs(
        self,
        keywords: str | Iterable | None = None,
        city_code: Optional[str] = None,
        max_pages: Optional[int] = None,
        industry: str = "",
        domain: str = "",
        job_role: str = "",
    ) -> Iterator[dict]:
        if keywords is None:
            keywords = ["python"]
        if isinstance(keywords, str):
            keywords = [keywords]
        pages = max_pages or self.max_pages

        for kw in keywords:
            # 允许传 (industry, domain, job_role, keyword) 这种四元组
            if isinstance(kw, (tuple, list)) and len(kw) == 4:
                kw_industry, kw_domain, kw_role, keyword = kw
            else:
                kw_industry, kw_domain, kw_role, keyword = industry, domain, job_role, kw

            # 行业/领域/岗位类别没传的时候就不要打印 " >  > " 这种空壳
            path = " > ".join(p for p in (kw_industry, kw_domain, kw_role) if p)
            print(f"\n爬取关键词: {keyword}" + (f" | {path}" if path else ""))

            for page in range(1, pages + 1):
                raw_list = self.fetch_jobs(keyword, page, city_code=city_code)
                if not raw_list:
                    print(f"第 {page} 页无数据或请求失败，停止翻页。")
                    break

                for raw in raw_list:
                    yield self.parse_job(raw, kw_industry, kw_domain, kw_role, keyword)

                print(f"第 {page} 页完成，{len(raw_list)} 条")
                time.sleep(random.uniform(self.min_sleep, self.max_sleep))

    def crawl_jobs(
        self,
        keywords: str | Iterable | None = None,
        city_code: Optional[str] = None,
        max_pages: Optional[int] = None,
        fields: Iterable[str] | None = None,
        **field_filters: Any,
    ) -> list[dict]:
        # industry / domain / job_role 是"给结果打的标签"（配合职位树用），
        # 不是筛选条件，所以从 field_filters 里拎出来单独传给 iter_jobs
        labels = {k: field_filters.pop(k) for k in ("industry", "domain", "job_role")
                  if k in field_filters}

        jobs = list(self.iter_jobs(keywords, city_code=city_code,
                                   max_pages=max_pages, **labels))

        if field_filters:
            jobs = self.filter_jobs(jobs, **field_filters)
        if fields:
            jobs = self.select_fields(jobs, fields)

        print(f"\n共 {len(jobs)} 条（未落盘，直接返回）")
        return jobs

    # 四、给智能体用：工具本体 + 工具列表
    def search_jobs(
        self,
        keywords: str,
        city_code: str = "489",
        max_pages: int = 1,
        limit: int = 10,
        job_type: Optional[str] = None,
        work_type: Optional[str] = None,
        degree: Optional[str] = None,
        skills: Optional[str] = None,
        fields: Optional[list[str]] = None,
    ) -> str:
        """按关键词检索岗位，返回 JSON 字符串

        max_pages 控制翻几页（每页 20 条），limit 控制最终返回几条；
        用户说“找两个岗位”时应该用 limit=2，而不是 max_pages=2。
        """
        params = JobSearchParams(
            keywords=keywords,
            city_code=city_code,
            max_pages=max_pages,
            limit=limit,
            job_type=job_type,
            work_type=work_type,
            degree=degree,
            skills=skills,
            fields=fields,
        )

        # 注意：这里先不加 fields，等校验完完整记录再裁字段
        # GetJobSchema 要 14 个字段全在，先裁了字段再校验必然报 Field required
        jobs = self.crawl_jobs(
            keywords=params.keywords,
            city_code=params.city_code,
            max_pages=params.max_pages,
            **params.filters,
        )

        # 拿一条完整记录对一遍格式，确认字段没缺（解析逻辑改了也能马上发现）
        if jobs:
            GetJobSchema(**jobs[0])

        # 校验通过后再按需裁字段，省上下文
        if params.fields:
            jobs = self.select_fields(jobs, params.fields)

        total = len(jobs)
        # limit 是“最终返回几条”，和 max_pages（翻几页）分开；
        # 再套一层 return_limit，防止调用方传得过大。
        limit = min(params.limit, self.return_limit)
        returned = jobs[:limit]
        return json.dumps(
            {
                "total": total,
                "returned": len(returned),
                "truncated": total > limit,
                "jobs": returned,
            },
            ensure_ascii=False,
        )

    def get_job_tools(self) -> list:
        return [
            StructuredTool.from_function(
                func=self.search_jobs,
                name="search_jobs",
                description=(
                    "按关键词检索招聘岗位（智联招聘）。"
                    "keywords 必填，例如 python、Java开发、数据分析；"
                    "city_code 传数字代码，489=全国（传城市名无效）；"
                    "max_pages 是翻页数，1~5，每页 20 条；"
                    "limit 是最终返回几条（1~30），用户说“找两个”就填 2，没说默认 10；"
                    "注意：“两个岗位”用 limit=2，不要填 max_pages=2；"
                    "还可按 job_type（岗位类型）/work_type（全职、兼职/临时、实习）"
                    "/degree（学历）/skills（技能，如 Django）进一步筛选；"
                    "fields 指定只返回哪些字段以节省上下文。"
                    "返回 JSON 字符串，含 total、returned 和 jobs。"
                ),
                args_schema=JobSearchParams,
            )
        ]


# 演示：直接把结果打出来（不写任何文件）
if __name__ == "__main__":
    tool = GetJobTool(max_pages=1)

    # 方式一：直接当方法调
    print("=== 直接调 search_jobs ===")
    print(tool.search_jobs(keywords="python", city_code="489",
                           fields=["job_name", "company", "salary", "city", "job_type"])[:400])

    # 方式二：拿工具列表，看智能体看到的入参
    print("\n=== 工具列表（智能体看到的东西）===")
    for t in tool.get_job_tools():
        print(f"  工具名: {t.name}")
        print(f"  入参字段: {list(t.args_schema.model_fields.keys())}")

    # 参数校验：故意传错，看会不会被拦
    print("\n=== 参数校验演示 ===")
    for bad in [{"keywords": "python", "city_code": "成都"},
                {"keywords": "python", "fields": ["job_name", "不存在的字段"]},
                {"keywords": "python", "max_pages": 99}]:
        try:
            tool.search_jobs(**bad)
            print(f"  {bad} -> 居然通过了")
        except Exception as e:
            first_line = str(e).strip().splitlines()[2] if len(str(e).splitlines()) > 2 else str(e)
            print(f"  {bad} -> 被拦下: {first_line.strip()[:70]}")
