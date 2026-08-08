from fastapi import APIRouter

from ai import LLM
from users.dao import UsersDao
from users.entity import CheckEntity
from users.service import UsersService



# 创建子路由对象
users_router = APIRouter()

@users_router.get(
    path='/sendEmail',
    # 接口简短摘要，显示在SwaggerUI的接口列表中
    summary='发送邮件',
    # 接口详细描述，显示在SwaggerUI的接口详情中
    description='给用户输入的邮箱号发送验证码，其中有个参数 email,表示用户输入的邮箱号信息',
    # 分组
    tags=['users'],
)
def send_email(email: str):
    # 调用服务层方法 --- 服务层方法的返回值在这里可以就是直接返回给客户端请求的响应数据
    ver_code = UsersService.send_email(email)
    return ver_code

@users_router.post(
    path='/Verification_Module',
    summary='验证模块',
    description='验证用户输入的验证码是否正确，其中有个参数 code,表示用户输入的验证码信息',
    tags=['users'],
)
def verification_module(verifycode: CheckEntity.VerifyCode):
    # 调用服务层方法
    flag = UsersService.Verification_Module(verifycode)
    return flag
    # return Verification_Module(code)

@users_router.get(
    path=r'/chat',
    summary='ai对话',
    description='''
        聊天
        访问路径：http://localhost:8000/users/chat
        请求参数；
            question: 用户问题
        返回值：
            流式输出 sse
    '''
)
def chat(question):
    # 加载模型
    llm = LLM.chatLLM
    # 聊天
    return {
        'code': 200,
        'msg': '成功',
        'data': llm.invoke([
            {'role': 'user', 'content': question}
        ]).content,
    }
