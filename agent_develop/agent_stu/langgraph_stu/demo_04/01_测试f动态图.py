from langchain_core.messages import HumanMessage
from langgraph_stu.demo_04.graph.email_agent04 import email_agent
import asyncio


async def test01():
    graph = email_agent()
    input = {
        'messages': [
            HumanMessage(content='给cyx发个邮箱，说今晚开会')
        ]
    }
    async for chunk, metadata in graph.astream(input, stream_mode='messages'):
        yield chunk.content


# 在做完一个智能体测试前先画流程图
def draw_graph():
    agent = email_agent()
    # 画图
    data = agent.get_graph().draw_mermaid_png()
    with open('动态路由图.png', 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    draw_graph()
    # async def test():
    #     async for rs in test01():
    #         print(rs, end='')
    # asyncio.run(test())