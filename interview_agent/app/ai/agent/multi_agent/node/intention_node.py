from langchain.agents import create_agent
from app.ai.agent.multi_agent.schema.intention_schema import IntentionSchema
from app.ai.agent.multi_agent.state.exam_state import ExamState
from app.ai.model.my_model import MyModel
from app.ai.prompt.prompt_builder import BuilderPromptYaml
from langchain_core.messages import AIMessage, HumanMessage
'''
    意图识别节点
'''
# 读取提示词文件
prompt = BuilderPromptYaml.get_prompt("intention_node.yaml")


def last_user_input(messages) -> str:
    """取最近一条用户消息

    不能用 messages[0]：第一轮之后 messages[0] 还是最初的输入，
    用户后来说的“给我 5 道题”根本没被读到，数量自然一直不对。
    """
    for m in reversed(messages or []):
        if isinstance(m, HumanMessage):
            return m.content if isinstance(m.content, str) else str(m.content)
    return ''


def intention_node(state: ExamState):
    # 获取用户输入的问题（最近一条用户消息）
    user_input = last_user_input(state.get('messages'))
    # 用远程模型做意图识别
    model = MyModel.get_model()
    # 创建智能体
    agent = create_agent(
        model=model,
        system_prompt=prompt,
        response_format=IntentionSchema
    )
    # 提问
    user_msg = {'messages': [{'role': 'user', 'content': user_input}]}
    rs = agent.invoke(user_msg)
    # 把输出结果转换成字典或者json
    data = rs['structured_response'].model_dump()
    ai_msg = f"\n意图识别成功，课程名称为:{data['course']}，课程数量为:{data['num']}\n"
    # 更新状态
    return {
        'messages': [AIMessage(content=ai_msg)],
        'course': data['course'],
        'total': data['num'],
        "exam_step": 'intention'
    }