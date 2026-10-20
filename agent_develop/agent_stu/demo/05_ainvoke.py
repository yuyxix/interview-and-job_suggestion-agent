from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
import asyncio

"""
    async 有两种用法：
        1. async def — 定义异步函数（协程函数）     
        当一个函数内部使用了异步操作（如 await、async for、async with）时，这个函数必须声明为 async def。
    await 用于等待一个协程（coroutine）执行完成，拿到返回值。
        判断方法：当你调用一个 async def 函数时，它不会立即执行，而是返回一个协程对象。要用 await 来等待它执行完并拿到结果。
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
    rs = await agent.invoke(human_msg)
    reply = rs['messages'][-1]['content']
    return reply


if __name__ == '__main__':
    question = '为什么会下雨'
    asyncio.run(create_email_agent(question))