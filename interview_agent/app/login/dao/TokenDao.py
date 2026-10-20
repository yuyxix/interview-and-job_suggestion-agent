from app.common import RedisUtil
from app.ai.utils.MySqlUtil import GetMysqlCon


def save_token(username, token: str):
    try:
        r = RedisUtil.get_redis_con()
        r.set(username, token, ex=1800)
        RedisUtil.close_redis_con(r)
        return {
            'code': 200,
            'msg': 'token存入成功',
            'data': None
        }
    except Exception as e:
        print(f'存入失败{e}')

def permission_dao(username: str):
    con = GetMysqlCon.get_mysql_con()
    cur = con.cursor()
    # 列名是 user_name（不是 username），跟你现有的表对齐
    sql = 'SELECT role_name FROM permission_info WHERE user_name=%s'
    cur.execute(sql, [username])
    result = cur.fetchone()
    GetMysqlCon.close_mysql_con(cur, con)
    return result

if __name__ == '__main__':
    print(permission_dao('cyx'))