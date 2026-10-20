from langchain_core.messages import HumanMessage
from langgraph_stu.demo_01.graph.email_agent01 import email_agent
import asyncio
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
graph = email_agent(memory)
config = {'configurable': {'thread_id': 1}}


async def test01():
    input = {
        'messages': [
            HumanMessage(content='给cyx发个邮箱，说今晚开会')
        ]
    }
    async for chunk, metadata in graph.astream(input, config, stream_mode='messages'):
        yield chunk.content


# 人工审核-修改
def test02():
    async def test():
        async for chunk in test01():
            print(chunk, end='')
    asyncio.run(test())
    # 获取拦截点
    state = graph.get_state(config)
    print(state)
    info = input('请输入修改邮箱的内容')
    graph.update_state(config, {'content': info})
    # 继续执行
    rs = graph.invoke(None, config)
    print(rs['messages'][-1].content)


if __name__ == '__main__':
    test02()