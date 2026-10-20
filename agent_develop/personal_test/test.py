from langchain_core.messages import HumanMessage
from graph.email_agent import email_agent
import asyncio


async def test01(query):
    graph = email_agent()
    input = {
        'messages': [
            HumanMessage(content=query)
        ]
    }
    async for chunk, metadata in graph.astream(input, stream_mode='messages'):
        yield chunk.content


def draw_graph():
    agent = email_agent()
    # 画图
    data = agent.get_graph().draw_mermaid_png()
    with open('条件图.png', 'wb') as f:
        f.write(data)


async def test(q):
    async for rs in test01(q):
        print(rs, end='')


if __name__ == '__main__':
    # draw_graph()
    q1 = '给cyx发个邮箱，说今晚开会'
    q2 = '你好，今天天气不错'
    asyncio.run(test(q2))
