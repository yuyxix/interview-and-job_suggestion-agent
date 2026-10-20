import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# 定义客户端所在目录
dirt = r'E:\workspace\agent_develop\agent_stu\mcp服务应用程序开发'
# 定义客户端的启动程序
p = '02_基于stdio协议的MCP服务端.py'
# 构建命令
c = StdioServerParameters(
    command='python',   # 编译命令
    cwd=dirt,   # 启动程序所在目录
    args=[p]    # 启动程序文件
)


# 定义异步函数
async def test():
    async with stdio_client(c) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()
            # 获取工具列表
            rs = await session.list_tools()
            print(rs)
            # 执行工具
            data = await session.call_tool('send_email_tool',{'to': '3278708004@qq.com', 'subject': '测试', 'content': '这是一封测试邮件'})
            print(data)
            print(data.structured_content['result'])
            # data = await session.call_tool('mysql_tool', {'p': {'sql': 'select * from agent_userinfo'}})
            # print(data.structured_content['result'])
if __name__ == '__main__':
    # stdio是本地协议，在客户端程序中就已经写好入口程序
    # 如果不启动服务器，可以在本地环境直接运行，即本地命令行，但是需要在本地命令行安装所有需要的库
    # 或者手动启动虚拟环境，在虚拟环境中运行程序
    asyncio.run(test())