from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
import asyncio
"""
    事件流可以避开漫长的等待，把ai正在处理的工作返回给用户
    让用户不必等待，而是可以看到ai的工作进行到哪一步了
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
    rs = agent.astream_events(human_msg, version='v2')
    async for event in rs:
        # 获取事件内容
        event_name = event['event']
        if event_name == 'on_chain_start':
            yield f'\n智能体开始工作...\n'
        elif event_name == 'on_chat_model_start':
            yield f'\n智能体开始思考...\n'
        elif event_name == 'on_chat_model_end':
            yield f'\n智能体结束思考...\n'
        elif event_name == 'on_chain_stream':
            yield f'\n智能体开始生成答案...\n'
        elif event_name == 'on_tool_start':
            # 获取工具名称
            tool_name = event['name']
            if tool_name == 'send_email_tool':
                yield f'\n正在发送邮件...\n'
        elif event_name == 'on_tool_end':
            # 获取工具返回值
            tool_output = event['data']['output'].content
            yield f'\n邮件已发送，内容为：{tool_output}\n'
        elif event_name == 'on_chat_model_stream':
            data = event['data']['chunk'].content
            if data:
                yield data

async def output():
    async for rs in create_email_agent(question):
        print(rs, end='')

if __name__ == '__main__':
    question = '给3278708004@qq.com这个邮箱发送你好'

    # 当函数是个异步函数，就要用异步库中的函数来执行函数，即 asyncio.run()
    asyncio.run(output())