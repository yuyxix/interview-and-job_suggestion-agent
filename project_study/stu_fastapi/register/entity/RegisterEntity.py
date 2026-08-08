from pydantic import BaseModel, Field

class VerifyCode(BaseModel):
    email:  str = Field(..., description="邮箱")
    code: str = Field(..., description="验证码")

class register(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
