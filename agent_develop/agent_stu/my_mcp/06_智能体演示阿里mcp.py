from langchain_core.messages import HumanMessage
from model.my_model import MyModel
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")


# 配置MCP客户端
# 在调用外部mcp时，根据官方提供的信息来判断使用什么协议
client = MultiServerMCPClient(
    {
        'mytool': {
            'transport': 'http',
            'url': 'https://dashscope.aliyuncs.com/api/v1/mcps/EnhancedSearch/mcp',
            'headers': {
                'Authorization': f'Bearer {api_key}'
            }
        }
    }
)


# 智能体创建
async def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_model()
    # 获取工具列表
    tool_list = await client.get_tools()
    # 定义一个工具
    # tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        --角色：你是一个聊天助手
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tool_list,
        system_prompt=prompt,
        debug=True  # 一般用于调试，生产环境必须设置为False
    )
    # 问题
    # 定义一个人类消息类型格式
    # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
    # 另一种定义方法
    human_msg = {'messages': [HumanMessage(content=question)]}
    rs = await agent.ainvoke(human_msg)
    reply = rs['messages'][-1].content
    return reply

if __name__ == '__main__':
    question = '请帮我检索一些关于人工智能岗位的招聘信息'
    print(asyncio.run(create_email_agent(question)))