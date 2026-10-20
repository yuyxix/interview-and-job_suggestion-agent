from langchain_core.messages import HumanMessage

from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent

# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_local_model()
    # 定义一个工具
    tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        一.角色：你是一个邮件发送助手
        二.任务：你需要根据用户的需求发送对应的邮件给对应的人
        三.规则：
                1. 你只能根据用户要求发送邮件，禁止做无关的回复,回答只能发邮件。
                2. 当邮件主题与内容不明确的话，请向用户咨询清楚
                3. 若用户输入问题与邮件发送无关，友善回答
                4. 若有邮箱格式问题，告知用户格式不正确
                四.输出：
                1.只能输出json格式
                2.json格式如下: {'output': "xxx"}
        五.实例：
                输入：天气不错
                输出：对不起，我只能发送邮件
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        debug=True  # 一般用于调试，生产环境必须设置为False
    )
    # 问题
    # 定义一个人类消息类型格式
    # human_msg = {"messages": [{'role': 'user'},{'content': question}]}
    # 另一种定义方法
    human_msg = {'messages': [HumanMessage(content=question)]}
    rs = agent.invoke(human_msg)
    reply = rs['messages'][-1].content
    return reply

if __name__ == '__main__':
    question1 = "今天天气不错"
    question2 = "请帮我给3278708004@qq.com发送邮件"
    question3 = "请帮我给123qq.com发送一个打招呼的邮件"
    print(create_email_agent(question1))