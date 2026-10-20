from langchain.tools import tool
from app.ai.tools.schema.mysql_schema import MySqlSchema
from app.ai.utils.MySqlUtil import GetMysqlCon


"""
    将数据库封装成agent的工具的好处：
        如果用户的问题多种多样，那么想要查询到email可能就需要多个方法来处理传入不同参数的情况
        所以直接用封装成工具，让模型理解用户的意图并且自己根据信息决定如何查询数据库
        这样可以提升复用性，但同时也就需要更多兜底的操作，以防止ai的失控
"""


@tool(args_schema=MySqlSchema)
def mysql_tool(sql: str) -> str:
    """
        执行sql语句查询
        规则：
            - 禁止生成 DELETE, UPDATE, INSERT, DROP, CREATE, ALTER 语句
    """
    con = None
    cur = None
    try:
        con = GetMysqlCon.get_mysql_con()
        cur = con.cursor()
        # 兜底操作
        if 'DELETE' in sql or 'UPDATE' in sql or 'INSERT' in sql or 'DROP' in sql or 'CREATE' in sql or 'ALTER' in sql:
            return '禁止执行删除、更新、插入、删除、创建、修改数据库结构语句'
        cur.execute(sql)
        # 事务提交，针对非查询操作
        # cur.commit()
        rs = cur.fetchall()
        return str(rs)
    except Exception as e:
        return str(e)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


if __name__ == '__main__':
    sql = 'select * from question_bank where question_subject="python" and question_id not in (1,2,3)  ORDER BY RAND() desc LIMIT 1'
    print(mysql_tool.invoke(sql))