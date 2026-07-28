# 封装数据库连接，关闭的工具
import pymysql

# 获取链接
def my_sql_conn():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='3278708004cyx',
        database='login',
        charset='utf8mb4',
        # 获取字典类型数据
        cursorclass=pymysql.cursors.DictCursor
    )

# 关闭连接
def mysql_close(cur, conn):
    cur.close()
    conn.close()