from fastapi import APIRouter
from app.register.entity.RegisterEntity import RegisterInfo, VerifyCode
from app.register.service import RegisterService
from app.register.service.RegisterService import register_server

register_router = APIRouter()

@register_router.get(
    path='/sendemail',
    summary='发送邮件',
    description='给用户输入的邮箱号发送验证码',
    tags=['register']
)
def send_email(email: str):
    ver_code = RegisterService.send_email(email)
    return ver_code

@register_router.post(
    path='/VerifyCode',
    summary='验证验证码',
    description='验证验证码是否正确',
    tags=['register'],
)
def verification_module(verify_code: VerifyCode):
    flag = RegisterService.verification_module(verify_code)
    return flag


@register_router.post(
    path='/register',
    summary='注册',
    description='通过邮箱号和验证码注册账号',
    tags=['register'],
)
def register_account(register_info: RegisterInfo):
    return register_server(register_info)
