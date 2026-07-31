import pymysql
import os
from dotenv import load_dotenv

load_dotenv()
# 获取链接
def get_mysql_conn():
    return pymysql.connect(
        # IP地址
        host=os.getenv('MYSQL_HOST'),
        # 端口号
        port=int(os.getenv('MYSQL_PORT')),
        # 数据库账户
        user=os.getenv('MYSQL_USER'),
        # 数据库账户对应的密码
        password=os.getenv('MYSQL_PASSWORD'),
        # 数据库名称
        database=os.getenv('MYSQL_DB'),
        # 字符集
        charset=os.getenv('MYSQL_CHARSET'),
        # 以dict的方式返回查询结果
        cursorclass=pymysql.cursors.DictCursor
        )

# 关闭连接
def close_mysql_conn(cursor, conn):
    cursor.close()
    conn.close()