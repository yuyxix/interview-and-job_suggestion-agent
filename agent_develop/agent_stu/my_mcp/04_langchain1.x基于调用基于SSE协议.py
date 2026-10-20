from langchain_core.messages import HumanMessage
from model.my_model import MyModel
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
# 配置MCP客户端,基于stdio协议配置
client01 = MultiServerMCPClient(
    {
        'mytool': {
            'transport': 'stdio',
            'command': 'python',
            'args': ['02_基于stdio协议的MCP服务端.py'],
            'cwd': r'E:\workspace\agent_develop\agent_stu\mcp服务应用程序开发'
        }
    }
)


# 智能体创建
async def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_local_model()
    # 获取工具列表
    tool_list = await client01.get_tools()
    # 定义一个工具
    # tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个邮件发送助手
        —工作：你需要根据用户的需求发送对应的邮件给对应的人
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
    question = '帮我给3278708004@qq.com这个邮箱发送一封邮件，通知他好好上课'
    print(asyncio.run(create_email_agent(question)))