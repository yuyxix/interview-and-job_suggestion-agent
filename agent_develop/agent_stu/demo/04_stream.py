from langchain_core.messages import HumanMessage

from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent

# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_model()
    # 定义一个工具
    tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个邮件发送助手
        —工作：你需要根据用户的需求发送对应的邮件给对应的人
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        debug=True  # 一般用于调试，生产环境必须设置为False
    )
    # 问题
    # 定义一个人类消息类型格式
    # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
    # 另一种定义方法
    human_msg = {'messages': [HumanMessage(content=question)]}
    # stream_mode='messages' 表示返回的是消息流
    rs = agent.stream(human_msg, stream_mode='messages')
    for aimsg, other in rs:
        if aimsg.content:
            print(aimsg.content)

if __name__ == '__main__':
    question = '为什么会下雨'
    create_email_agent(question)