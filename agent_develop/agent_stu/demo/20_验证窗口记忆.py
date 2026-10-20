from langchain_core.messages import HumanMessage
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from memory.manage.session_manage import SessionManage


# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_local_model()
    # 定义一个工具
    # tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个聊天助手
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        # tools=tools,
        system_prompt=prompt,
        debug=True  # 一般用于调试，生产环境必须设置为False
    )

    # 创建会话管理器
    session_manager = SessionManage('001')
    # 添加窗口记忆
    session_manager.save('user', question)
    memory_prompt = session_manager.build_prompt()
    human_msg = {'messages': [HumanMessage(content=question), memory_prompt]}
    # 构建记忆的提示词
    rs = agent.invoke(human_msg)
    session_manager.save('ai', rs['messages'][-1].content)
    return rs['messages'][-1].content


if __name__ == '__main__':
    question1 = '我叫张三，今年23岁'
    question2 = '我喜欢打篮球'
    question3 = '我在学习python'
    question4 = '我是谁，今年多大了'
    question5 = '我在学习什么'
    print(create_email_agent(question5))