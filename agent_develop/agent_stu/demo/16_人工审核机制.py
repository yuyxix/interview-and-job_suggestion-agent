from langchain_core.messages import HumanMessage
from langchain.agents.middleware import HumanInTheLoopMiddleware
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

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
    memory = InMemorySaver()

    # 定义人工审核中间键
    review_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            'send_email': {
                # 是否允许操作方式，决策
                "allowed_decisions": ['approve', 'reject', 'edit'],
                # 自定义提示
                'description': '邮件发送需要人工审核，请确认邮件内容是否正确'
            }
        },
        # 公共提示前缀
        description_prefix='[人工审核]'
    )
    # 定义检查点
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        debug=True,  # 一般用于调试，生产环境必须设置为False
        middleware=[review_middleware],
        checkpointer=memory
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
    print(rs)
    d = rs['__interrupt__']
    if d:
        print('需要人工审核')
    else:
        print('模型不支持')

if __name__ == '__main__':
    question = '帮我给3278708004@qq.com这个邮箱发送一封邮件，通知他好好上课'
    print(create_email_agent(question, 1))