from pydantic import BaseModel, Field

class VerifyCode(BaseModel):
    email:  str = Field(..., description="邮箱")
    code: str = Field(..., description="验证码")