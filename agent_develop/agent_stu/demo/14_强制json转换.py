from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from pydantic import BaseModel, Field
import json

class CodeFormat(BaseModel):
    data: str = Field(..., description="验证码")
    code: str = Field(..., description="状态码，200表示成功，500表示失败")
    msg: str = Field(..., description="提示信息")

# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_model()
    # 定义一个工具
    tools = [send_email]
    # 创建提示词, 系统提示词
    # 强制转换需要通过提示词加兜底，以防模型生成不符合规范
    prompt = """
        --角色：你是一个邮件发送助手
        --工作：
            --理解用户需求
            --生成一个不规则的四位数的数字作为验证码
            --根据用户需求发送邮件
        --规则：
            -验证码必须是四位
            -如果邮件发送成功，状态码为200，提示信息为'邮件发送成功'
            -如果失败，状态码为500，提示信息为验证码'邮件发送失败'
        --输出：
            输出格式必须是
                {
                "data": "验证码", 
                "code": "状态码", 
                "msg": "提示信息"
                }
            - 只输出 JSON
                - 不允许输出 Markdown
                - 不允许输出 ```json
                - 不允许输出解释说明
                - 不允许输出多个 JSON
                - 不允许输出任何额外文字
                - JSON 必须能够被 `json.loads()` 正确解析
        --实例：
            -输入：邮箱是123456789@qq.com，发送邮件
            -输出：验证码，200，邮件发送成功
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        response_format=CodeFormat,
        debug=True  # 一般用于调试，生产环境必须设置为False
    )
    # 问题
    # 定义一个人类消息类型格式
    # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
    # 另一种定义方法
    human_msg = {'messages': [HumanMessage(content=question)]}
    rs = agent.invoke(human_msg)
    print(rs)

# 不确定的情况下应该对仍有较大概率发生的情况二次兜底，如```json，因为大模型输出通常是markdown格式
def get_json(text):
    if "```json" in text:
        data = text.replace('```json', '').replace('```', '')
        return data
    else:
        return text




if __name__ == '__main__':
    question = '给3278708004@qq.com这个邮箱发一个验证码'
    create_email_agent(question)