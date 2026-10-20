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
    async with Client('https://mcp.api-inference.modelscope.net/9f05e88fba9149/mcp') as client:
        # 获取工具列表
        rs = await client.list_tools()
        print(rs)

if __name__ == '__main__':
    asyncio.run(test())
