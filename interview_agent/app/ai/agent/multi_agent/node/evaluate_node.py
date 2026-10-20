import asyncio

from langchain.agents import create_agent
from langgraph.config import get_stream_writer
from app.ai.agent.multi_agent.state.exam_state import ExamState
from langchain_core.messages import AIMessage
from app.ai.model.my_model import MyModel
from app.ai.prompt.prompt_builder import BuilderPromptYaml
"""
    评价节点
    流式输出实现：评价节点使用 get_stream_writer() 实现实时流式输出，
    评分结果通过 LangGraph 的 `custom` stream mode 直接推送到前端，无需等待整个评价完成。
"""

prompt = BuilderPromptYaml.get_prompt("evaluate_node.yaml")


def build_evaluation_data(state: ExamState) -> str:
    """把题目、用户答案、数据库标准答案按题目配对

    之前是三个独立列表，模型要自己按 id 对齐，很容易忽略标准答案或配错。
    这里直接拼成：
        第1题：...
        用户答案：...
        标准答案：...
    """
    questions = state.get('question', []) or []
    user_answers = state.get('user_answer', []) or []
    sure_answers = state.get('sure_answer', []) or []

    user_map = {
        item.get('question_id'): item.get('answer', '')
        for item in user_answers
        if isinstance(item, dict)
    }
    sure_map = {
        item.get('id'): item.get('answer', '')
        for item in sure_answers
        if isinstance(item, dict)
    }

    lines = []
    for i, item in enumerate(questions, 1):
        if not isinstance(item, dict):
            continue
        qid = item.get('id')
        question = item.get('question', '')
        user_answer = user_map.get(qid, '（未作答）')
        standard_answer = sure_map.get(qid) or item.get('answer') or '（题库中没有标准答案）'
        lines.append(f'第{i}题：{question}')
        lines.append(f'用户答案：{user_answer}')
        lines.append(f'标准答案：{standard_answer}')
        lines.append('')

    return '\n'.join(lines) or '没有可评价的题目。'


async def evaluate_node(state: ExamState):
    model = MyModel.get_model()

    # 历史记忆：让评价参考"这个用户以前的表现"（比如同一知识点上次也不会）
    # 评价没有"单个问题"，用课程 + 面试当检索问句
    memory_ctx = ''
    try:
        from app.ai.agent.multi_agent.memory.manage.memory_manager import (
            MemoryManager, get_collection,
        )
        mm = MemoryManager(state.get('memory_id'), state.get('user_id'),
                           collection=get_collection())

        # 记忆上下文：用户画像 + 最多 2 条摘要 + 2 条长期召回（别的会话）
        #             + 3 条窗口记忆；超长时自动降级成 1 条摘要
        probe = f"{state.get('course', '')} 面试 用户表现 弱项"
        memory_ctx = await asyncio.to_thread(
            mm.get_context,
            question=probe,
            exclude_session_id=mm.memory_id,
            window_messages=3,
            summary_limit=2,
            recall_n=2,
        )
    except Exception as e:
        # 记忆挂了照样能评价
        print(f'[evaluate_node] 历史记忆获取失败: {type(e).__name__}: {e}')

    system_prompt = prompt
    if memory_ctx:
        system_prompt += (
            '\n\n【历史记忆（该用户以前的面试表现，评价时可参考，不要照抄）】\n'
            + memory_ctx
        )

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
    )
    data = build_evaluation_data(state)
    msg = {'messages': [{'role': 'user', 'content': data}]}
    result_list = []
    # 获取langgraph的流式输出器
    writer = get_stream_writer()
    # 先推一个分隔线：评价内容和上一条"答案已记录"是拼在同一条 AI 消息里的，
    # 不隔开的话前端会显示成"答案已记录 ## 第1题：..."黏成一坨
    writer({'type': 'evaluation', 'content': '\n\n---\n\n'})
    # 流式执行，实时输出结果
    async for c, m in agent.astream(msg, stream_mode='messages'):
        if c.content:
            result_list.append(c.content)
            # 实时推送到graph的流中
            writer({'type': 'evaluation', 'content': c.content})
    result = ''.join(result_list)
    return {
        # 注意字段名要和 ExamState 里声明的一致，否则会被 langgraph 静默丢弃
        'evaluation': result,
        # 评价内容上面已经通过 writer() 逐字流式推给前端了，
        # 这里只留一个标记，不要再塞一遍完整结果，否则前端会显示两遍
        'messages': [AIMessage(content='\n评价完成\n')],
        'exam_step': 'end'
    }