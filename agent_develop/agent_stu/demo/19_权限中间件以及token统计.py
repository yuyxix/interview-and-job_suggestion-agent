from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents.middleware import before_agent, after_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent


@before_agent
def get_user_id(state: AgentState, time: Runtime):
    # 用户id
    user_id = time.execution_info.thread_id
    # 并且可以通过这一步，结合数据库来查询用户的部门等等，来分配权限
    if user_id not in range(0, 10):
        raise ValueError("您没有权限访问")
    return {}


@after_agent
def count_token(state: AgentState, time: Runtime):
    """
        真实业务中，可以配合redis来统计不同用户的token使用情况并记录
        即第一次对话存入token用量，之后每一次对话都将redis中的token用量取出来加上新的token用量
        再重新存入，推荐以hash的形式存储
    """
    print(state['messages'])
    msg = state['messages']
    input_token = 0
    output_token = 0
    total_token = 0
    if msg[1].usage_metadata:
        input_token += msg[1].usage_metadata['input_tokens']
        output_token += msg[1].usage_metadata['output_tokens']
        total_token += msg[1].usage_metadata['total_tokens']
    return {
        'messages': [AIMessage(content=f'输入token：{input_token}，输出token：{output_token}，总token：{total_token}')]
    }


# 智能体创建
def create_email_agent(question, user_id):
    # 定义一个大模型
    model = MyModel.get_local_model()
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
            middleware=[get_user_id, count_token]
        )
        # 问题
        # 定义一个人类消息类型格式
        # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
        # 另一种定义方法
        human_msg = {'messages': [HumanMessage(content=question)]}
        config = {'configurable': {'thread_id': user_id}}
        rs = agent.invoke(human_msg, config)
        print(rs['messages'][-1].content)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    question1 = '你好'
    print(create_email_agent(question1, 1))