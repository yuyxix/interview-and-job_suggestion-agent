from app.ai.utils.MySqlUtil import GetMysqlCon


def list_users():
    """用户列表：以 user_info 为准，左连权限表拿角色"""
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT u.user_id, u.user_name, u.email, "
            "COALESCE(p.role_name, 'user') AS role_name "
            "FROM `user_info` u "
            "LEFT JOIN `permission_info` p ON p.user_id = u.user_id "
            "ORDER BY u.user_id"
        )
        return cur.fetchall()
    finally:
        GetMysqlCon.close_mysql_con(cur, con)


def get_user(username):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT u.user_id, u.user_name, u.email, "
            "COALESCE(p.role_name, 'user') AS role_name "
            "FROM `user_info` u "
            "LEFT JOIN `permission_info` p ON p.user_id = u.user_id "
            "WHERE u.user_name=%s",
            (username,),
        )
        return cur.fetchone()
    finally:
        GetMysqlCon.close_mysql_con(cur, con)


def get_user_by_id(user_id):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT u.user_id, u.user_name, u.email, "
            "COALESCE(p.role_name, 'user') AS role_name "
            "FROM `user_info` u "
            "LEFT JOIN `permission_info` p ON p.user_id = u.user_id "
            "WHERE u.user_id=%s",
            (user_id,),
        )
        return cur.fetchone()
    finally:
        GetMysqlCon.close_mysql_con(cur, con)


def delete_user(username):
    """删除用户：user_info / register_info / permission_info 一起删

    返回被删用户的 {user_id, user_name, email}，不存在返回 None。
    （只删前两张表的话，user_info 里账号还在，仍能登录）
    """
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        cur.execute(
            'SELECT user_id, user_name, email FROM `user_info` WHERE user_name=%s',
            (username,),
        )
        user = cur.fetchone()
        if not user:
            return None

        cur.execute('DELETE FROM `user_info` WHERE user_id=%s', (user['user_id'],))
        cur.execute('DELETE FROM `permission_info` WHERE user_id=%s', (user['user_id'],))
        if user.get('email'):
            cur.execute(
                'DELETE FROM `register_info` WHERE username=%s OR email=%s',
                (username, user['email']),
            )
        else:
            cur.execute('DELETE FROM `register_info` WHERE username=%s', (username,))

        con.commit()
        return user
    except Exception as e:
        print(f'删除用户失败{e}')
        con.rollback()
        return None
    finally:
        # 参数顺序是 (cursor, connection)，原来写反了
        GetMysqlCon.close_mysql_con(cur, con)


def change_roles(role_name, username):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    try:
        cur.execute(
            'SELECT user_id, user_name FROM `user_info` WHERE user_name=%s',
            (username,),
        )
        user = cur.fetchone()
        if not user:
            return 0

        # 没有权限记录就补一条；有就更新角色
        cur.execute(
            "INSERT INTO `permission_info` (user_id, user_name, role_name) "
            "VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE role_name=VALUES(role_name), "
            "user_name=VALUES(user_name)",
            (user['user_id'], user['user_name'], role_name),
        )
        con.commit()
        return 1
    except Exception as e:
        print(f'修改用户角色失败{e}')
        con.rollback()
        return 0
    finally:
        GetMysqlCon.close_mysql_con(cur, con)