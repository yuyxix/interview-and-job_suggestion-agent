from common import MySQLUtil


def check_email(email):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    # 编写sql语句
    sql = 'SELECT * FROM users WHERE email=%s'
    # 执行sql语句
    cur.execute(sql, [email])
    # 获取查询结果
    results = cur.fetchall()
    # 关闭连接
    MySQLUtil.close_mysql_conn(cur, conn)
    # 返回结果
    return results


if __name__ == '__main__':
    print(check_email('3278708004@qq.com'))