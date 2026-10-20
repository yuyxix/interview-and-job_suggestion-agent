from langchain_core.messages import HumanMessage
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
import redis


# 连接redis服务
client = redis.StrictRedis(host='localhost', port=6379, db=2)


@before_model
# Runtime 对象是 LangGraph 框架在调用你的函数之前就在外面创建好的，
# 然后通过函数参数time传进来的。
def model_limit_before_middleware(state: AgentState, time: Runtime):
    print(time)
    # 从当前正在运行的对话中得到用户id
    user_id = time.execution_info.thread_id
    print(f'用户id: {user_id}')
    # 查询用户模型调用次数
    num = 3
    # 自定义键名
    key = f'limit: {user_id}'
    data = client.get(key)
    print(data)
    if data is None:
        return {}
    else:
        data = int(data.decode())
        if data >= num:
            raise ValueError("用户模型调用次数超过限制")
    return {}


@after_model
def model_limit_after_middleware(state: AgentState, time: Runtime):
    user_id = time.execution_info.thread_id
    print(f'用户id: {user_id}')
    # 自定义键名
    key = f'limit: {user_id}'
    # 设置自增
    client.incr(key, 1)
    # 设置失效时间
    client.expire(key, 120)
    print(f'用户{user_id}模型使用次数增加1')
    return {}


# 智能体创建
def create_email_agent(question, user_id):
    # 定义一个大模型
    model = MyModel.get_model()
    # 定义一个工具
    tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个邮件发送助手 
        —工作：你需要根据用户的需求发送对应的邮件给对应的人
    """

    try:
        # 定义检查点
        memory = InMemorySaver()
        # 创建智能体
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
            debug=True,  # 一般用于调试，生产环境必须设置为False
            checkpointer=memory,
            middleware=[]
        )
        # 问题
        # 定义一个人类消息类型格式
        # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
        # 另一种定义方法
        human_msg = {'messages': [HumanMessage(content=question)]}
        config = {'configurable': {'thread_id': user_id}}
        # 中间键要引入记忆机制，因为会有中断状态，所以需要保存记忆，记忆状态信息
        #
        rs = agent.invoke(human_msg, config)
        print(rs['messages'][-1].content)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    question1 = '我要赌博'
    print(create_email_agent(question1, 1))