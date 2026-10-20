from pydantic import BaseModel, Field

class VerifyCode(BaseModel):
    email: str = Field(..., description='邮箱')
    code: str = Field(..., description='验证码')

class RegisterInfo(BaseModel):
    username: str = Field(..., description='用户名')
    email: str = Field(..., description='注册邮箱')
    password: str = Field(..., description='注册密码')
