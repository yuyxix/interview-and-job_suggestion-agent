import asyncio
import json
import re

from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from app.ai.tools.get_job_tool import GetJobTool
from app.ai.tools.schema.get_job_schema import JobParamExtraction
from app.ai.prompt.prompt_builder import BuilderPromptYaml
from app.ai.agent.multi_agent.memory.save.profile_memory import ProfileMemory
from langgraph.config import get_stream_writer
from app.ai.agent.multi_agent.state.exam_state import ExamState
tool = GetJobTool()
params_prompt = BuilderPromptYaml.get_prompt('get_job_params.yaml')


_CN_NUM = {
    '一': 1, '两': 2, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
}


def requested_count(text: str) -> int:
    text = text or ''
    patterns = [
        r'(?:找|要|来|给|出|推荐|查|搜)[^0-9一二两三四五六七八九十]{0,6}'
        r'(\d+|[一二两三四五六七八九十])\s*(?:个|条|份|道)',
        r'(\d+|[一二两三四五六七八九十])\s*(?:个|条|份|道)\s*'
        r'(?:岗位|工作|职位|题|面试题)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        token = match.group(1)
        if token.isdigit():
            return int(token)
        return _CN_NUM.get(token, 0)
    return 0


def extract_job_params(question: str, profile: str = ''):
    # 用户没说清楚方向时，把画像一起交给模型，让它从画像里选岗位方向。
    content = question
    if profile:
        content = f'用户画像：\n{profile}\n\n用户当前需求：\n{question}'

    # 优先用远程模型提取参数：本地 Ollama 偶尔会卡住不按指令走，
    # 远程模型在意图识别里已经验证可用；本地只作为备用。
    for get_model in (MyModel.get_model, MyModel.get_local_model):
        try:
            agent = create_agent(
                model=get_model(),
                system_prompt=params_prompt,
                response_format=JobParamExtraction,
            )
            rs = agent.invoke({'messages': [{'role': 'user', 'content': content}]})
            data = rs['structured_response'].model_dump()
            keywords = (data.get('keywords') or '').strip()
            if keywords:
                data['keywords'] = keywords
                return data
            # 模型明确表示没有可提取的方向：直接返回 None，
            # 不再让本地模型猜一个关键词，避免编造岗位方向。
            return None
        except Exception as e:
            print(f'[get_job] 参数提取失败: {type(e).__name__}: {e}')
    return None


def format_jobs(tool_json: str, max_jobs: int = 0) -> str:
    try:
        data = json.loads(tool_json)
    except Exception:
        return ''
    jobs = data.get('jobs') or []
    if max_jobs > 0:
        jobs = jobs[:max_jobs]
    if not jobs:
        return '没有检索到符合条件的岗位，可以换个关键词试试。'

    lines = [f'找到以下 {len(jobs)} 个岗位：']
    for i, job in enumerate(jobs, 1):
        # 每条写成一行，避免 Markdown 把换行折叠掉；字段用“；”分隔
        lines.append(
            f'{i}. 岗位名：{job.get("job_name") or "未提供"}；'
            f'公司：{job.get("company") or "未提供"}；'
            f'薪资：{job.get("salary") or "未提供"}；'
            f'城市：{job.get("city") or "未提供"}；'
            f'经验：{job.get("experience") or "未提供"}；'
            f'学历：{job.get("degree") or "未提供"}；'
            f'技能：{job.get("skills") or "未提供"}'
        )
    return '\n'.join(lines)


async def get_job_node(state: ExamState):
    # 图调节点时，第一个参数永远是整个状态（不是字符串！）
    question = state['messages'][-1].content
    user_id = state.get('user_id')

    # 读取用户画像：用户没有明确岗位方向时，用它来推荐。
    profile = ''
    try:
        if user_id:
            profile = await asyncio.to_thread(
                lambda: (ProfileMemory(user_id).query() or '').strip()
            )
    except Exception as e:
        print(f'[get_job] 画像读取失败: {type(e).__name__}: {e}')

    stream_writer = get_stream_writer()

    # 提取检索参数：有画像时一并交给模型，让它从画像里选方向。
    try:
        params = await asyncio.wait_for(
            asyncio.to_thread(extract_job_params, question, profile),
            timeout=60,
        )
    except Exception as e:
        print(f'[get_job] 参数提取超时/失败: {type(e).__name__}: {e}')
        params = None

    if not params:
        # 没有画像、也没有明确方向：让用户补充岗位信息。
        # 有画像但模型仍没提取出来：也让用户补充，避免瞎搜。
        if profile:
            msg = '我暂时没能确定你想找的岗位方向，请补充一下岗位方向、城市或经验要求，我再帮你检索。'
        else:
            msg = ('我还不了解你的求职方向，请告诉我你想找的岗位方向'
                   '（例如 Java、前端、人工智能）、城市或经验要求，我再帮你检索。')
        stream_writer({'type': 'job', 'content': msg})
        return {'messages': [AIMessage(content='')], 'exam_step': 'job'}

    try:
        output = await asyncio.to_thread(tool.search_jobs, **params)
    except Exception as e:
        print(f'[get_job] 检索失败: {type(e).__name__}: {e}')
        stream_writer({'type': 'job', 'content': '岗位检索没有成功执行，请稍后再试。'})
        return {'messages': [AIMessage(content='')], 'exam_step': 'job'}

    # 用工具 JSON 生成完整岗位列表；用户说“找两个”时按原话截断到 2 条。
    formatted = format_jobs(output, requested_count(question))
    if formatted:
        stream_writer({'type': 'job', 'content': formatted})
    else:
        stream_writer({'type': 'job', 'content': '岗位检索完成，但结果解析失败，请重新提问试试。'})

    return {
        # 最终结果已经通过 writer 推给前端了；这里用空消息占位，
        # 避免前端在岗位列表后面多出一句“岗位检索完毕”。
        'messages': [AIMessage(content='')],
        'exam_step': 'job'
    }
if __name__ == '__main__':
    # print(get_job_node('帮我找5个python技术相关的工作'))
    pass