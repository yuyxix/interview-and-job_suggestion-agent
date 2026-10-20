import asyncio
from app.ai.agent.multi_agent.memory.manage.memory_manager import MemoryManager, get_collection
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
from app.ai.agent.multi_agent.state.exam_state import ExamState
from langchain_core.messages import AIMessage, HumanMessage
from app.ai.model.my_model import MyModel
from app.ai.prompt.prompt_builder import BuilderPromptYaml
from langchain.agents.middleware import ModelCallLimitMiddleware
"""
    聊天+记忆节点
"""
prompt = BuilderPromptYaml.get_prompt("chat_node.yaml")


def load_memory_context(state: ExamState) -> str:

    try:
        mm = MemoryManager(state.get('memory_id'), state.get('user_id'),
                           collection=get_collection())
    except Exception as e:
        print(f'[chat_node] 记忆管理器创建失败: {type(e).__name__}: {e}')
        return ''
    try:
        return mm.get_context(
            question=state['messages'][-1].content,
            exclude_session_id=mm.memory_id,
            window_messages=3,
            summary_limit=2,
            recall_n=2,
        )
    except Exception as e:
        print(f'[chat_node] 记忆上下文组装失败: {type(e).__name__}: {e}')
        return ''


# 用户当前这句话是否在追问"上一个问题 / 上一句 / 刚才说了什么"
_HISTORY_QUESTION_MARKERS = (
    '上一个问题', '上一条问题', '上一题', '刚才的问题', '前一个问题',
    '上一个提问', '上一句', '上一轮', '前一句', '刚才问', '刚才说',
    '之前问', '刚刚问',
)
_HISTORY_QUESTION_WORDS = ('什么', '啥', '哪', '内容')


def is_history_question(text: str) -> bool:
    """判断当前输入是不是在追问历史

    只有这类输入才需要附带"上一问"提示。否则普通输入（比如"我擅长python"）
    也会被模型当成"请回答上一个问题"。
    """
    text = (text or '').strip()
    if not text:
        return False
    has_marker = any(m in text for m in _HISTORY_QUESTION_MARKERS)
    has_question = any(w in text for w in _HISTORY_QUESTION_WORDS) \
        or text.endswith(('?', '？'))
    return has_marker and has_question


def build_user_msg(state: ExamState, memory_ctx: str = '',
                   recent_rounds: int = 3) -> dict:
    messages = state['messages']
    current = messages[-1]
    # 只取最近 N 轮（一问一答算一轮，所以是 2N 条），且不含当前这句。
    # messages 会一直累加，全塞进去迟早把本地模型的 4096 上下文撑爆。
    keep = recent_rounds * 2
    history = messages[-(keep + 1):-1] if len(messages) > keep + 1 else messages[:-1]

    # 当前这句之前，用户最后问过的那个问题
    prev_question = next(
        (m.content for m in reversed(history) if isinstance(m, HumanMessage)),
        None
    )

    current_text = current.content if isinstance(current.content, str) else str(current.content)
    current_text = current_text.strip()

    # 当前这句单独标注，和历史分开
    text = f'（用户当前问题，不在历史里）{current_text}'
    # ★ 只有当前这句确实在追问历史时，才附带"上一问"提示。
    #   否则模型会把提示当成当前问题的答案，出现"用户说我擅长python，
    #   它却回答上一个问题"这种串台。
    if prev_question and is_history_question(current_text):
        text += f'\n（提示：用户在这之前最后问过的问题是）{prev_question}'
    if memory_ctx:
        # 只加一句说明，别再套一层标题（memory_ctx 自己已经带小标题了）
        text = f'（以下是背景信息，仅供参考，不是当前对话，回答里不要提及）\n{memory_ctx}\n\n' + text

    return {'messages': [*history, HumanMessage(content=text)]}


async def answer_with(model, user_msg) -> str:
    """跑一次对话，边生成边把结果流式推给前端，最后返回完整正文"""
    agent = create_agent(
        model=model,
        system_prompt=prompt,
        middleware=[
            ModelCallLimitMiddleware(
                thread_limit=3,
                exit_behavior='end'
            )
        ]
    )
    writer = get_stream_writer()
    # 先推一个分隔线：这次的回复和上一条消息（"答案已记录"/"第N道题"）是拼在同一条
    # AI 消息里的，不隔开前端会显示成"答案已记录 xxx"黏成一坨
    writer({'type': 'chat', 'content': '\n\n---\n\n'})

    parts = []
    async for c, m in agent.astream(user_msg, stream_mode='messages'):
        if c.content:
            parts.append(c.content)
            # 实时推送到 graph 的流中
            writer({'type': 'chat', 'content': c.content})
    return ''.join(parts)


async def chat_node(state: ExamState):
    # 历史记忆：同步 IO（Redis 窗口 + Chroma 召回），丢到线程里别卡住事件循环
    memory_ctx = await asyncio.to_thread(load_memory_context, state)
    # 消息只整理一次，两个分支共用（原来两个分支各写了一遍，改动容易漏）
    user_msg = build_user_msg(state, memory_ctx, recent_rounds=2)

    # 聊天优先用远程模型：本地 qwen2.5:7b 在“回答过上一个问题”之后，
    # 容易顺着上一轮的模式继续回答历史，即使当前问题已经换了。
    # 远程模型对“当前问题优先”的指令跟随更稳定，失败再切本地兜底。
    try:
        answer = await answer_with(MyModel.get_model(), user_msg)
    except Exception as e:
        print(f'远程模型失败，切换本地兜底：{type(e).__name__}: {e}')
        try:
            answer = await answer_with(MyModel.get_local_model(), user_msg)
        except Exception as e:
            print(f'服务器超时：{type(e).__name__}: {e}')
            return {'messages': [AIMessage(content='\n请求超时，请重新尝试\n')], 'exam_step': 'chat'}

    # 正文已经通过 writer 流式推给前端；这里把完整正文写回 state，
    # 让下一轮对话的历史里能看到这一轮 AI 的回答。
    # （ExamGraph 里会跳过这条整消息的前端推送，避免重复显示）
    return {
        'messages': [AIMessage(content=answer)],
        'exam_step': 'chat'
    }
