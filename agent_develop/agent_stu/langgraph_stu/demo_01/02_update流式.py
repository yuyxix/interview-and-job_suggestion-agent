from langchain_core.messages import HumanMessage
from langgraph_stu.demo_01.graph.email_agent01 import email_agent
import asyncio


async def test01():
    graph = email_agent()
    input = {
        'messages': [
            HumanMessage(content='给cyx发个邮箱，说今晚开会')
        ]
    }
    async for chunk in graph.astream(input, stream_mode='updates'):
        yield '\n'
        yield chunk
# message模式更侧重输出token流，直接返回结果
# updates比起messages更细粒度，可以实时看到中间节点状态更新过程

if __name__ == '__main__':
    # draw_graph()
    async def test():
        async for rs in test01():
            print(rs, end='')
    asyncio.run(test())