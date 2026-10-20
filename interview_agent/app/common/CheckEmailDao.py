from app.ai.utils.MySqlUtil import GetMysqlCon


def check_email(email: str):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    # 添加信息的sql语句
    sql = 'SELECT * FROM `user_info` WHERE email=%s'
    # 执行
    cur.execute(sql, [email])
    result = cur.fetchone()
    GetMysqlCon.close_mysql_con(cur, con)
    return result


if __name__ == '__main__':
    print(check_email('3278708004@qq.com'))