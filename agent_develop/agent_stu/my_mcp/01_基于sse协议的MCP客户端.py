import asyncio
from fastmcp import Client


async def test():
    # 定义客户端
    # 这里的客户端协议要与启动的客户端的协议一致
    async with Client('http://localhost:9000/sse') as client:
        # 获取工具列表
        rs = await client.list_tools()
        print(rs)
        # 调用工具
        data = await client.call_tool('send_email_tool', {'to': '3278708004@qq.com', 'subject': '测试', 'content': '这是一封测试邮件'})
        print(data.structured_content['result'])
        data = await client.call_tool('mysql_tool', {'p': {'sql': 'select * from agent_userinfo'}})
        print(data.structured_content['result'])
if __name__ == '__main__':
    asyncio.run(test())