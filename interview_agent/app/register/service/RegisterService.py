import os
import random
import re
import smtplib
import string
from email.mime.text import MIMEText
from app.common import RedisUtil, CheckEmailDao
from app.register.dao.RegisterDao import add_email, add_account, add_permission
from dotenv import load_dotenv


load_dotenv()


def send_email(email: str):
    flag = False
    # 判断输入邮箱格式
    if re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+[a-zA-Z0-9._-]$', email):
        flag = True
    if not flag:
        return {
            'code': 500,
            'msg': '邮箱格式错误,请重新输入',
            'data': None,
        }
    # 发送邮件
    code = ''
    code_list = [i for i in string.digits] + [i for i in string.ascii_letters]
    for i in random.choices(code_list, k=6):
        code += i

    # 发件方
    sender = os.getenv('SENDER_EMAIL')
    sender_pwd = os.getenv('SENDER_EMAIL_PASSWORD')
    sub = '验证码'
    content = f'您的验证码是{code},有效时间60s'

    # 创建邮件的对象
    message = MIMEText(content, 'plain', 'utf-8')
    # 添加信息在message对象中
    message['From'] = sender
    message['To'] = email
    message['Subject'] = sub
    # 构造发送邮件的对象
    try:
        smtp = smtplib.SMTP(
            # .env 里的键叫 SMTP_HOST（原来写的 SMTP_SERVER 取到 None，SMTP 会直接报错）
            host=os.getenv('SMTP_HOST'),
            port=int(os.getenv('SMTP_PORT'))
        )
        # 开启邮件发送服务tls
        smtp.starttls()
        # 验证授权码
        smtp.login(sender, sender_pwd)
        # 发送邮件
        smtp.sendmail(sender, email, message.as_string())
        # 发送成功后退出
        smtp.quit()
        # 将验证码存入到redis中
        r = RedisUtil.get_redis_con()
        r.set(email, code, ex=60)  # 60s后过期
        RedisUtil.close_redis_con(r)
        return {
            'code': 200,
            'msg': '验证码已发送,请查收',
            'data': None,
        }
    except Exception as e:
        # 发信失败要如实返回失败 —— 原来这里会掉到下面的 return 200，
        # 前端以为发出去了，但 Redis 里没存验证码，下一步校验必然失败，很难查
        print(f'发送失败{e}')
        return {
            'code': 500,
            'msg': f'验证码发送失败：{e}',
            'data': None,
        }


# 验证验证码服务
def verification_module(verify_code):
    email = verify_code.email
    code = verify_code.code
    r = RedisUtil.get_redis_con()
    verify_code = r.get(email)
    if code == verify_code:
        flag = check_email(email)
        if flag:
            return {
                'code': 500,
                'msg': '邮箱已存在,请直接登录',
                'data': None,
            }
        if not flag:
            if code == verify_code:
                add_email(email)
                return {
                    'code': 200,
                    'msg': '验证码正确',
                    'data': None,
                }
            if code != verify_code:
                return {
                    'code': 500,
                    'msg': '验证码错误',
                    'data': None,
                }
            if code == None:
                return {
                    'code': 500,
                    'msg': '验证码已过期',
                    'data': None,
                }

    # ★ 验证码不对（或已过期）时，上面那个 if 整块都不成立 → 函数走到末尾返回 None
    #   → 前端拿到空响应，等于"没有任何提示"（这就是"验证码输错了没提示"的原因）
    return {
        'code': 500,
        'msg': '验证码错误或已过期，请重新获取',
        'data': None,
    }


def check_email(email):
    flag = CheckEmailDao.check_email(email)
    return flag


def register_server(RegisterInfo):
    username = RegisterInfo.username
    password = RegisterInfo.password

    try:
        result = add_account(RegisterInfo)
        if result['code'] == 200:
            add_permission(RegisterInfo)
            return {
                'code': 200,
                'msg': '注册成功',
                'data': None,
            }
        if result['code'] == 400:
            return {
                'code': 400,
                'msg': '用户名已存在，请重试',
                'data': None,
            }
    except Exception as e:
        print(f'注册失败{e}')
        return {
            'code': 500,
            'msg': '注册失败',
            'data': None,
        }

