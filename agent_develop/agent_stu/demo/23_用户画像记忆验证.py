
from model.my_model import MyModel
from langchain.agents import create_agent
from memory.manage.session_manage import SessionManage
from langchain_core.messages import HumanMessage
from memory.manage.memory_manage import MemoryManager


# 智能体创建
def create_email_agent(question):
    # 定义一个大模型
    model = MyModel.get_local_model()
    # 定义一个工具
    # tools = [send_email]
    # 创建提示词, 系统提示词
    prompt = """
        -角色：你是一个聊天助手
        -回复中不必解释摘要相关的内容和历史对话的内容，只需自行根据历史记录和摘要回答即可
        - 
    """
    # 创建智能体
    agent = create_agent(
        model=model,
        # tools=tools,
        system_prompt=prompt
    )

    # 创建会话管理器
    session_manager = SessionManage('001', 1)
    # 添加窗口记忆
    session_manager.save('user', question)
    memory_prompt = session_manager.build_prompt(1, question)
    human_msg = {'messages': [HumanMessage(content=question), memory_prompt]}
    # 构建记忆的提示词
    rs = agent.invoke(human_msg)
    session_manager.save('ai', rs['messages'][-1].content)
    # 更新记忆
    memory_manager = MemoryManager(session_manager)
    memory_manager.update(1, question)
    return rs['messages'][-1].content


if __name__ == '__main__':
    question1 = '我叫张三，今年23岁'
    question2 = '我喜欢打篮球'
    question3 = '我在学习python'
    question4 = '我在学习什么'
    question5 = '我擅长什么'
    # for query in [question1, question2, question3, question4, question5]:
    #     print('='*50)
    print(create_email_agent(question5))