from langchain_core.messages import HumanMessage
from tool.amap_driver_tool import driver_tool
from tool.send_email_tool import send_email
from model.my_model import MyModel
from langchain.agents import create_agent
from prompt.builder_prompt_yaml import BuilderPromptYaml

# 智能体创建
def personal_agent(question):
    # 定义一个大模型
    model = MyModel.get_local_model()
    # 定义一个工具
    tools = [send_email, driver_tool]
    # 创建提示词, 系统提示词
    prompt = BuilderPromptYaml.get_prompt('send_email_agent.yaml')
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
    question = "告诉我成都到绵阳的路线"
    print(personal_agent(question))