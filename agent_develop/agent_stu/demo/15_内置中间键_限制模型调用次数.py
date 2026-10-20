from langchain_core.messages import HumanMessage
from langchain.agents.middleware import ModelCallLimitMiddleware
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent

# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_model()
    # 定义一个工具
    tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个邮件发送助手
        —工作：你需要根据用户的需求发送对应的邮件给对应的人
    """

    # 创建中间键，限制模型访问次数
    # 一方面可以防范恶意攻击，一方面可以让大模型有限制的多次自我调用，防止陷入死循环
    model_limit = ModelCallLimitMiddleware(
        # 限制访问次数
        thread_limit=2,
        # 达到次数限制后，结束会话·
        exit_behavior='end'
    )

    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        debug=True,  # 一般用于调试，生产环境必须设置为False
        middleware=[model_limit]
    )
    # 问题
    # 定义一个人类消息类型格式
    # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
    # 另一种定义方法
    human_msg = {'messages': [HumanMessage(content=question)]}
    rs = agent.invoke(human_msg)
    reply = rs['messages'][-1]['content']
    return reply

if __name__ == '__main__':
    question = '帮我给3278708004@qq.com这个邮箱发送一封邮件，通知他好好上课'
    print(create_email_agent(question))