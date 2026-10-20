import asyncio
from fastmcp import Client
import os
from dotenv import load_dotenv
load_dotenv()
"""
    可以在一些模型网站采用别人做好的mcp的工具
"""
api_key = os.getenv("DASHSCOPE_API_KEY")


async def test():
    # 定义客户端
    async with Client('https://dashscope.aliyuncs.com/api/v1/mcps/WebFetch/mcp', auth=f'Bearer {api_key}') as client:
        # 获取工具列表
        rs = await client.list_tools()
        print(rs)
        data = await client.call_tool('web_fetch', {'url': 'https://www.swpu.edu.cn/'})
        print(data)
        print(data.content[0].text)
if __name__ == '__main__':
    asyncio.run(test())
