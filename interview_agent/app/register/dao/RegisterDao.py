from app.ai.utils.MySqlUtil import GetMysqlCon
from app.register.entity.RegisterEntity import RegisterInfo
from app.register.util.HashSecretUtil import hash_password


# 定义往数据库增加账户的方法
def add_email(email: str):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    # 添加信息的sql语句
    try:
        # 指定列名插入（原来写的是 4 个位置值，跟表结构对不上）
        sql = 'INSERT INTO `register_info` (email) VALUES (%s)'
        # 执行
        cur.execute(sql, [email])
        # 提交新增
        con.commit()
        # 返回新增账户的id
        return cur.lastrowid
    except Exception as e:
        print(f'新增邮箱失败{e}')
        con.rollback()
        return 0
    finally:
        GetMysqlCon.close_mysql_con(cur, con)


def add_account_tool():
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    sql = 'SELECT username FROM `register_info`'
    cur.execute(sql)
    result = cur.fetchall()
    GetMysqlCon.close_mysql_con(cur, con)
    return result


def add_account(register_info: RegisterInfo):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    # 添加信息的sql语句
    email = register_info.email
    password = register_info.password
    hashed_password = hash_password(password)
    try:
        sql = 'UPDATE `register_info` SET username=%s, password=%s WHERE email=%s'
        usernames = add_account_tool()
        for item in usernames:
            if register_info.username in item:
                GetMysqlCon.close_mysql_con(cur, con)
                return {
                    'code': 400,
                    'message': '用户名已存在',
                    'data': None
                }
        # 更新暂存表 register_info
        cur.execute(sql, [register_info.username, hashed_password, email])

        # ★ 关键一步：登录查的是 user_info（CheckEmailDao 里那张表），必须写它
        #   原来只写了 register_info，所以注册完根本登录不了
        cur.execute(
            'INSERT INTO `user_info` (user_name, email, password) VALUES (%s, %s, %s)',
            [register_info.username, email, hashed_password]
        )
        new_user_id = cur.lastrowid
        # 回填 register_info.user_id —— 下一步 add_permission 要从这里取 user_id
        cur.execute('UPDATE `register_info` SET user_id=%s WHERE email=%s', [new_user_id, email])

        # 提交新增
        con.commit()
        # 返回新增账户的id
        return {
            'code': 200,
            'msg': '新增账户成功',
            'data': new_user_id
        }
    except Exception as e:
        print(f'新增账户失败{e}')
        con.rollback()
        return 0
    finally:
        GetMysqlCon.close_mysql_con(cur, con)


def add_permission_tool(username):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    sql = 'SELECT user_id FROM `register_info` WHERE username = %s'
    cur.execute(sql, [username])
    result = cur.fetchall()
    GetMysqlCon.close_mysql_con(cur, con)
    return result


def add_permission(register_info: RegisterInfo):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        username = register_info.username
        user_id = add_permission_tool(username)[0]['user_id']
        sql = 'INSERT INTO `permission_info` (user_id, user_name, role_name) VALUES (%s, %s, %s)'
        cur.execute(sql, [user_id, username, 'user'])
        con.commit()
        return {
            'code': 200,
            'msg': '新增权限成功',
            'data': None
        }
    except Exception as e:
        print(f'新增权限失败{e}')
        con.rollback()
        return 2
    finally:
        GetMysqlCon.close_mysql_con(cur, con)