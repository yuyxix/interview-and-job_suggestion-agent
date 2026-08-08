# from fastapi import APIRouter
# from register.entity import RegisterEntity
# from register.service import RegisterService
# from users.service import UsersService
#
# register_router = APIRouter()
#
# @register_router.get(
#     path='/register',
#     # 接口简短摘要，显示在SwaggerUI的接口列表中
#     summary='发送邮件',
#     # 接口详细描述，显示在SwaggerUI的接口详情中
#     description='给用户输入的邮箱号发送验证码，其中有个参数 email,表示用户输入的邮箱号信息',
#     # 分组
#     tags=['users'],
# )
# def send_email(email: str):
#     # 调用服务层方法 --- 服务层方法的返回值在这里可以就是直接返回给客户端请求的响应数据
#     ver_code = UsersService.send_email(email)
#     return ver_code
#
# @register_router.post(
#     path='/Verification_Module',
#     summary='验证模块',
#     description='验证用户输入的验证码是否正确，其中有个参数 code,表示用户输入的验证码信息',
#     tags=['users'],
# )
# def verification_module(verifycode: RegisterEntity.VerifyCode):
#     # 调用服务层方法
#     flag = RegisterService.Verification_Module(verifycode)
#     return flag
#
# @register_router.post(
#     path='/RegisterModule',
#     summary='注册模块',
#     description='用户注册，其中有个实体参数 , 接受注册信息，包括账号密码',
# )
# def register_module(register: RegisterEntity.register):
