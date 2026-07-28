# 操作数据库的文件
from users.utils import MySQLUtils

# 根据用户名查询用户信息
def find_users_by_username(username):
    # 获取连接对象
    conn = MySQLUtils.my_sql_conn()
    # 获取游标对象
    cur = conn.cursor()
    # 数据库操作
    sql = 'select * from user where username = %s'
    # 执行
    cur.execute(sql, [username])
    # 获取结果
    result = cur.fetchall()
    # 关闭连接，先开的先关，后开的后关
    MySQLUtils.mysql_close(cur, conn)
    # 返回结果
    return result

if __name__ == '__main__':
    print(find_users_by_username('admin'))
