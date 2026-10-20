from langchain.agents import create_agent

from langgraph_stu.demo_03.state.email_state03 import EmailState
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from model.my_model import MyModel

"""
    意图识别节点
"""


# 响应参数
class InternetResponse(BaseModel):
    name: str = Field(..., description="姓名")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")


def internet_node(state: EmailState):
    print(f'state: {state}')
    # 获取用户问题
    model = MyModel.get_local_model()
    prompt = """
        一.角色：你是一个意图识别助手
        二.任务：
            -理解用户需求
            -根据用户问题，提取姓名，主题和内容
        三.规则
            -姓名，邮箱主题，邮件不能为空
        四.输出
            -输出以下内容：{'name': 'xx', 'subject': 'xx', 'content': 'xx'}
        五.实例
            -用户输入：给张三发邮件，说今晚开会
            -输出：{'name': '张三', 'subject': '开会通知', 'content': '今晚开会'}
    """
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=prompt,
        response_format=InternetResponse,
        debug=True
    )
    msg = {'messages': [{'role': 'user', 'content': state['messages'][0].content}]}
    # 获取结果
    rs = agent.invoke(msg)
    print(rs)
    # 把响应结果转换为字典
    json = rs['structured_response'].model_dump()
    # 定义result，即ai返回的内容
    ai_msg = f'\n意图节点识别成功：\n 姓名：{json["name"]} \n 主题：{json["subject"]} \n 内容：{json["content"]}'
    # 只返回当前节点修改的状态信息
    return {
        'messages': [AIMessage(content=ai_msg)],
        'name': json['name'],
        'subject': json['subject'],
        'content': json['content']
    }