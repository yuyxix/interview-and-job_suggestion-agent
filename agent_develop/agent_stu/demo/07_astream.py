from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
import asyncio

"""
    agent.astream() 返回的不是协程，而是一个异步迭代器（async iterator），
    所以用 async for 来遍历，而不是 await。
    当你调用的某个方法/函数返回的是一个异步迭代器或异步生成器对象时，就需要用 async for 来遍历它。
    总的来说，如果是async函数，就会返回一个异步的结果，如果是迭代器之类的，就要用 async for等方法来取结果。
    要不返回的就是一个协程对象，需要用await来取值
"""


# 智能体创建
async def create_email_agent(question):
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
    human_msg = {'messages': [HumanMessage(content=question)]}
    rs = agent.astream(human_msg, stream_mode='messages')
    async for aimsg, other in rs:
        if aimsg.content:
            yield aimsg.content

if __name__ == '__main__':
    question = '为什么会下雨'
    async def test():
        async for rs in create_email_agent(question):
            print(rs, end='')

    # 当函数是个异步函数，就要用异步库中的函数来执行函数，即 asyncio.run()
    asyncio.run(test())