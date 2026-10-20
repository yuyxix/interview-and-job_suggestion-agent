from psycopg_pool import ConnectionPool


"""
    在需要进行多次类似读写数据库之类的操作的时候，
    需要多次创建链接，也就意味着需要频繁的关闭连接
    所以使用连接池来管理数据库连接 ，一次性先创建好多个连接存放着
    需要的时候直接拿出来用，用完了重新创建，可以大大提高效率
"""


# 配置数据库连接池
pool = ConnectionPool(
    conninfo='host=127.0.0.1 '
             'port=5432 '
             'dbname=postgres '
             'user=postgres '
             'password=3278708004cyx',
    # 连接池中存放的最大连接数，生产环境通常是20个，min_size同理
    max_size=20,
    min_size=10
)


class SummaryMemory:
    def __init__(self, session_id):
        self.session_id = session_id

    # 保存摘要
    def save(self, summary: str):
        with pool.connection() as con:
            with con.cursor() as cur:
                sql = f"INSERT INTO conversation_summary(session_id, summary) VALUES('{self.session_id}', '{summary}') ON CONFLICT(session_id)DO UPDATE SET summary=EXCLUDED.summary, update_time=NOW()"
                cur.execute(sql)
                # 提交事务
                con.commit()

    # 查询
    def query(self):
        with pool.connection() as con:
            with con.cursor() as cur:
                sql = f"select summary from conversation_summary where session_id = '{self.session_id}'"
                cur.execute(sql)
                # 查询单个值
                rs = cur.fetchone()
                if rs:
                    return rs[0]
                else:
                    return ""


if __name__ == '__main__':
    s = SummaryMemory('002')
    print(s.query())
    print(type(s.query()))