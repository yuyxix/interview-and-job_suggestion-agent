import random
import time
from email.mime.text import MIMEText
from users.dao import UsersDao
import os
from common import RedisUtil
from dotenv import load_dotenv
import smtplib
from common.RedisUtil import get_redis_conn
from users.entity import CheckEntity

load_dotenv()

# 发送邮件
def send_email(email: str):
    flag = False
    # 1.验证邮箱号是否输出注册过的用户
    # isinstance(a, b) 返回布尔值， 判定a是否是b的实例
    print(UsersDao.MySQLUtil.get_mysql_conn())
    if isinstance(UsersDao.check_email(email), list):
        flag = True
        print(flag)
    # 根据结果判定是否需要发邮件
    # 不发邮件
    if not flag:
        return {
            'code': 500,
            'msg': '邮箱账号不存在',
            'data': None,
        }
    # 发邮件
    # 随机生成四位数验证码
    code = ''
    for i in range(4):
        # 随机生成一个0-9的数字
        code += str(int(random.random() * 10))

    sender = os.getenv('SENDER_EMAIL') # 发送方
    sender_pwd = os.getenv('SENDER_EMAIL_PASSWORD')  # 发送方授权码
    subject = '验证码来了'  # 邮件主题
    content = f'你的验证码为：{code}，过期时间为：60s'

    # 创建邮件对象 --- 写发送邮件的信息在这个对象里面
    message = MIMEText(content, 'plain', 'utf-8')
    # 添加内容在message中
    message['From'] = sender # 发送方
    message['To'] = email  # 接收方
    message['Subject'] = subject   # 邮件主题

    try:
        # 构造发送邮件的对象
        smtp = smtplib.SMTP(
            host=os.getenv('SMTP_HOST'),
            port=int(os.getenv('SMTP_PORT')),
        )
        # 开启邮件发送服务 TLS
        smtp.starttls()
        # 验证发送方和发送方的授权码是否能对上
        smtp.login(sender, sender_pwd)
        # 发送邮件 -- sendmail 发送邮件的方法: 发送方, 接收方, 邮件对象
        smtp.sendmail(sender, email, message.as_string())
        # 发送成功退出
        smtp.quit()
        # 把验证码存入到redis中
        r = RedisUtil.get_redis_conn()
        # redis存入数据通过key,value格式 --- 取值通过key
        r.set(email, code, ex=60)  # 60s后过期， key: email value: code
        RedisUtil.close_redis_conn(r)

        return {
            'code': 200,
            'msg': '发送成功',
            'data': code,
        }
    except Exception as e:
        print(e)


    return {
        'code': 200,
        'msg': '发送成功',
        'data': None,
    }

# 定义一个验证函数接收并验证验证码
def Verification_Module(VerifyCode):
    email = VerifyCode.email
    code = VerifyCode.code
    r = get_redis_conn()
    ver_code = r.get(email)
    print(ver_code)
    print(type(ver_code))
    if code == ver_code:
        return {
            'code': 200,
            'msg': '验证成功',
            'data': None,
        }
    if code != ver_code:
        return {
            'code': 500,
            'msg': '验证码错误，请重试',
            'data': None,
        }
    if code == None:
        return {
            'code': 500,
            'msg': '验证码已过期，请重新获取',
            'data': None,
        }

# def Verification_Module(code):
#     r = get_redis_conn()
#     ver_code = r.get(email)
#     print(ver_code)
#     print(type(ver_code))
#     if code == ver_code:
#         return {
#             'code': 200,
#             'msg': '验证成功',
#             'data': None,
#         }
#     elif code != ver_code:
#         return {
#             'code': 500,
#             'msg': '验证码错误，请重试',
#             'data': None,
#         }
#     elif code == None:
#         return {
#             'code': 500,
#             'msg': '验证码已过期，请重新获取',
#             'data': None,
#         }
