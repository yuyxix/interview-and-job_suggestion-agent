# 逻辑处理文件 --- 核心实现功能代码的位置

from users.dao import UserDao

# 登录
def login(users):
    username = users.username
    password = users.password
    if not (username and password):
        return {
            'code': 500,
            'msg': '用户名或密码不能为空',
            'data': None
                }
    # 根据用户名查询用户信息
    result = UserDao.find_users_by_username(username)
    if not result:
        return {
                'code': 500,
                'msg': '账号不存在',
                'data': None
                }
    # 判断密码
    if not (password != result[0]['password']):
        return {
                'code': 500,
                'msg': '密码错误',
                'data': None
                }
    # 返回结果
    return {
            'code': 200,
            'msg': '登陆成功',
            'data': None
            }