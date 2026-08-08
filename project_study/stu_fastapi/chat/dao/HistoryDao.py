from common import MySQLUtil

# 查询历史记录菜单栏
def query_history_menu(username):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = "SELECT historyId, question, createTime FROM history WHERE username=%s AND parentId=0;;"
    cur.execute(sql, [username])
    result = cur.fetchall()
    MySQLUtil.close_mysql_conn(cur, conn)
    return result

# 查询某一条详细对话记录
def conversation_log(historyId):
    conn = MySQLUtil.get_mysql_conn()
    cur = conn.cursor()
    sql = 'SELECT question, answer FROM history WHERE historyId=%s OR parentId=%s ORDER BY historyId ASC'
    cur.execute(sql, [historyId, historyId])
    result = cur.fetchall()
    MySQLUtil.close_mysql_conn(cur, conn)
    return result
