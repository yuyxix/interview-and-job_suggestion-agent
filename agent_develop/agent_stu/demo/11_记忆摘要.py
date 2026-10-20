from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware


# 创建内存记忆监测点
memory = InMemorySaver()
# 定义一个大模型
model = MyModel.get_local_model()
# 定义一个工具
tools = [send_email]
# 创建提示词, 系统提示词
prompt = '你是一个智能助手'

# 定义摘要提示词
summary_prompt = """
    一 角色：你是一个邮件发送助手
    二 任务：
        - 主要负责提取用户的姓名
        - 以第三人称方式书写
    
    历史对话：
    {messages}
"""

# 定义摘要中间键配置
# 存储消息会把工具也存进去
summary = SummarizationMiddleware(
    model=model,
    # 设置阈值，即messages超过多少token，就会开始进行摘要，生产环境一般是1000~3000甚至3000往上
    # 另一种写法：trigger = [{"token": 4000}, {"messages": 20}， {{"token": 3000}, {"messages": 15}}]
    # 满足任意一组条件且组内条件都满足时，就会开始进行摘要，相当于把keep和keep合二为一了
    trigger=('tokens', 20),
    # 指保留最近的几轮对话，生产环境一般会保留多轮对话，建议20及以上
    keep=('messages', 1),
    summary_prompt=summary_prompt,
    # 限制摘要总结的token数量
    trim_tokens_to_summarize=4000
)

# 创建智能体
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=prompt,
    checkpointer=memory,
    # 中间键配置，可以有多个
    middleware=[summary]
)

# 智能体创建
def create_agent(question, user_id):
    human_msg = {'messages': [HumanMessage(content=question)]}
    config = {'configurable': {'thread_id': user_id}}
    rs = agent.invoke(human_msg, config)
    reply = rs['messages'][-1].content
    return reply

# 这是一个可以查看记忆状态的函数
def print_memory(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state = agent.get_state(config)
    messages = state.values.get("messages", [])
    print("\n================ 当前记忆状态 ================")
    print("消息数量：", len(messages))
    for i, message in enumerate(messages):
        print(f"\n--- Message {i + 1} ---")
        print("类型：", type(message).__name__)
        # 只打印前500个字符，避免输出太长
        content = str(message.content)
        print("内容：")
        print(content[:500])
    print("==============================================\n")


if __name__ == '__main__':

    q = [
        "1+1等于多少？",
        "我的名字叫张三，我是一名Java程序员。",
        "我今年23岁，目前正在学习LangChain和LangGraph。",
        "10+20等于多少？",
        "我的第一个问题是什么？",  # 测试记忆保留
        "我是谁？多少岁了，目前在学习什么"
    ]
    for i in range(len(q)):
        res = create_agent(q[i], 1)
        print(f"第{i + 1}个问题:")
        print(res)
    print("==============打印摘要记忆=============")
    print_memory(1)