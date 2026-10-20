from app.common import CheckEmailDao
from app.login.dao import TokenDao
from app.login.dao.TokenDao import save_token
from app.login.util.JWTUtil import create_token
from app.register.util.HashSecretUtil import verify_password


def check_account(email, password):
    info = CheckEmailDao.check_email(email)
    # 邮箱不存在时 info 是 None —— 原来直接 info['username'] 会 TypeError
    if not info:
        return {
            'code': 400,
            'msg': '邮箱不存在',
            'data': None
        }

    username = info['user_name']        # 表里的列叫 user_name（不是 username）
    user_id = info['user_id']
    roles = TokenDao.permission_dao(username)
    role_name = roles['role_name'] if roles else 'user'
    hashed_password = info['password']

    flag = verify_password(password, hashed_password)
    if flag is False:
        return {
            'code': 400,
            'msg': '密码错误',
            'data': None
        }

    token = create_token({'user_id': user_id, 'username': username, 'role_name': role_name})
    save_token(username, token)
    return {
        'code': 200,
        'msg': '登录成功',
        'data': {
            # user_id 要给前端：记忆是按 (user_id, memory_id) 隔离存的，
            # 前端必须带上它，否则记忆接口会拒绝写入（空值会让所有人的记忆混在一起）
            'user_id': user_id,
            'username': info['user_name'],
            'email': info['email'],
            # 前端据此决定登录后进管理后台还是聊天页
            'role_name': role_name,
            'token': token
        }
    }