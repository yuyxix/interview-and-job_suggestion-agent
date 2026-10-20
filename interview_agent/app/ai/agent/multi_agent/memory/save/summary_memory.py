from psycopg_pool import ConnectionPool

# 数据库连接池，用于应对频繁写入
pool = ConnectionPool(
    conninfo='host=127.0.0.1 '
             'port=5432 '
             'dbname=postgres '
             'user=postgres '
             'password=3278708004cyx',
    max_size=20,
    min_size=10,
)


class SummaryMemory:
    def __init__(self, session_id, user_id=None):
        # 隔离维度是 (user_id, session_id)：只按 session_id 的话，
        # 万一 session_id 传错/串号，摘要就写到别人的会话上了
        #
        # ★ 统一转成字符串：PG 里这两列是 text，拿 int 去 where 比对会直接报
        #   operator does not exist: text = integer（跟 Chroma 那个类型坑是一类问题）
        self.session_id = str(session_id) if session_id is not None else None
        self.user_id = str(user_id) if user_id is not None else None

    # 保存摘要
    def save(self, summary: str):
        with pool.connection() as con:
            with con.cursor() as cur:
                # 顺便改成参数化：摘要里带单引号的话，原来的 f-string 拼 SQL 会直接报错
                cur.execute(
                    "INSERT INTO conversation_summary(user_id, session_id, summary) "
                    "VALUES(%s, %s, %s) "
                    "ON CONFLICT(user_id, session_id) DO UPDATE "
                    "SET summary = EXCLUDED.summary, update_time = NOW()",
                    (self.user_id, self.session_id, summary),
                )
                con.commit()

    def query(self):
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "SELECT summary FROM conversation_summary "
                    "WHERE user_id = %s AND session_id = %s",
                    (self.user_id, self.session_id),
                )
                # 查询单个值
                rs = cur.fetchone()
                if rs:
                    return rs[0]
                else:
                    return ""

    # 查询该用户最近的 N 条摘要（当前会话优先，其次其它会话）
    def query_recent(self, limit: int = 2) -> list:
        """拼上下文用：返回 [{'session_id':..., 'summary':...}, ...]

        摘要按 (user_id, session_id) 存，一个会话一条；
        先保证当前会话的摘要排在最前面，再用其它会话的补足 limit 条。
        没有摘要就返回空列表。
        """
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "SELECT session_id, summary FROM conversation_summary "
                    "WHERE user_id = %s AND COALESCE(summary, '') <> '' "
                    "ORDER BY CASE WHEN session_id = %s THEN 0 ELSE 1 END, "
                    "update_time DESC "
                    "LIMIT %s",
                    (self.user_id, self.session_id, limit),
                )
                rows = cur.fetchall()
        return [
            {'session_id': row[0], 'summary': row[1]}
            for row in rows
        ]

    # 删除这段会话的摘要（删会话历史时一起清）
    def delete(self):
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "DELETE FROM conversation_summary WHERE user_id = %s AND session_id = %s",
                    (self.user_id, self.session_id),
                )
                con.commit()
        return True