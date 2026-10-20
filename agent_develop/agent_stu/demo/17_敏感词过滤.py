from langchain_core.messages import HumanMessage
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.runtime import Runtime
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
import re
from langchain_core.messages import AIMessage

"""
    过滤黄赌毒信息
"""


@before_model
def word_filter_middleware(state: AgentState, time: Runtime):
    print('验证是否在模型调用之前执行')
    print(state)
    word_list = ['赌博', '嫖娼', '吸毒']
    input_content = state['messages'][0].content
    for word in word_list:
        if word in input_content:
            raise ValueError(f'输入包含非法内容,不允许生成')
    return time


"""
    也可以定义after_model，让组件在模型调用之后执行
"""

# 屏蔽敏感词
@after_model
def word_ping_middleware(state: AgentState, time: Runtime):
    print('验证是否在模型调用之后执行')
    print(state)
    input_content = state['messages'][1].content
    word_list = ['赌博', '嫖娼', '吸毒']
    for word in word_list:
        if word in input_content:
            # 获取过滤后的内容
            input_content = re.sub(word, '***', input_content)
            return {
                'messages': [AIMessage(content=input_content)]
            }
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
        # 创建智能体
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
            debug=True,  # 一般用于调试，生产环境必须设置为False
            middleware=[word_ping_middleware],
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