from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

"""
    要把agent的创建全局化，并实现单例
    即在需要记忆的对话在同一个agent实例中，才能实现内存记忆
    否则相当于每循环一次都会重新创建一个agent对象，无法进行内存记忆
    
"""
# 创建内存记忆监测点
memory = InMemorySaver()
# 定义一个大模型
model = MyModel.get_local_model()
# 定义一个工具
tools = [send_email]
# 创建提示词, 系统提示词
prompt = '你是一个智能助手'
# 创建智能体
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=prompt,
    checkpointer=memory,
)


# 智能体创建
def create_email_agent(question, user_id):
    human_msg = {'messages': [HumanMessage(content=question)]}
    config = {'configurable': {'thread_id': user_id}}
    rs = agent.invoke(human_msg, config)
    reply = rs['messages'][-1].content
    return reply


if __name__ == '__main__':
    # 定义一个问题列表
    q_list = [
        '我叫张三',
        '我今年22岁',
        '我是谁，我多大'
    ]
    for i in range(len(q_list)):
        print(f'第{i+1}个问题：')
        print(create_email_agent(q_list[i], 1))