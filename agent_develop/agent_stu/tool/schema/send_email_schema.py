from pydantic import BaseModel, Field

# 定义工具参数的校验类
class EmailParams(BaseModel):
    # 定义收件人
    to: str = Field(..., description="收件人的邮箱")
    # 邮件主题
    subject: str = Field(..., description="邮件主题，即对邮件正文的一句话总结")
    # 正文
    content: str = Field(..., description="邮件正文，根据用户需求决定")
