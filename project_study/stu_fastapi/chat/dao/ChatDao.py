from common import MySQLUtil
'''
    查询操作不需要做事务管理
    增删改操作需要做事务管理
    操作成功 --- commit提交事务
    操作失败 --- rollack 回滚事务，不执行当前操作
'''

def save_conversation_result(username, question, answer, parentId):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "insert into `history` values(null, %s, %s, %s, %s, now())"
        cur.execute(sql, [username, question, answer, parentId])
        conn.commit()
        # 返回当前新增数据的主键自增id --- history_id
        return cur.lastrowid
    except Exception as e:
        print(f'新增会话结果失败：{e}')
        conn.rollback()  # 回滚操作
        return 0
    finally:
        MySQLUtil.close_mysql_conn(cur, conn)


def delete_history(history_id):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "delete from `history` where historyId = %s"
        cur.execute(sql, [history_id])
        conn.commit()
        return None
    except Exception as e:
        print(f'删除会话记录失败：{e}')
        conn.rollback()
        return 0
    finally:
        MySQLUtil.close_mysql_conn(cur, conn)

def delete_history_tool(historyId):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = 'SELECT * FROM `history` WHERE historyId = %s'
    cur.execute(sql, [historyId])
    result = cur.fetchall()
    MySQLUtil.close_mysql_conn(cur, conn)
    return result


# def delete_history_tool(historyId):
#     conn = MySQLUtil.get_mysql_conn()
#     cur = conn.cursor()
#     sql = 'SELECT * FROM `history`'
#     cur.execute(sql, [historyId])
#     result = cur.fetchall()
#     MySQLUtil.close_mysql_conn(cur, conn)
#     return result

if __name__ == '__main__':
    pass
