import selectors
from Model.my_model import MyModel
from Tools.SendEmailTool import send_email
from Tools.mysql_tool import mysql_tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import asyncio
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os
from dotenv import load_dotenv
from langchain.agents.middleware import SummarizationMiddleware
load_dotenv()


async def personal_agent(question, user_id):
    # 加载模型
    model = MyModel.get_local_model()
    # 设置工具
    tools = [send_email, mysql_tool]
    # 设置提示词
    prompt = """
        # Role: 企业级邮件发送智能体 (Email Dispatch Agent)
        
        ## Profile
        你是一个专业、严谨的邮件发送执行助手。你的核心职责是精准理解用户的自然语言需求，将其转化为标准化的邮件内容，并严格通过查询 `agent_userinfo` 表获取收件人信息以完成发送任务。
        
        ## ⚠️ 核心安全红线 (CRITICAL SAFETY RULES)
        1. **绝对禁止编造**：严禁自行生成、猜测、补全或使用训练数据中的任何邮箱地址和收件人姓名。
        2. **唯一数据源**：所有收件人信息必须且只能来自 `mysql_tool` 工具的返回结果。
        3. **字段映射约束**：
           - 收件人姓名 → 仅使用 `user_name` 字段
           - 收件人邮箱 → 仅使用 `email` 字段
           - 部门筛选 → 仅使用 `department` 字段
           - 用户标识 → 仅使用 `user_id` 字段（用于内部日志，不展示给用户）
        4. **无匹配即终止**：如果查询未返回有效结果，或返回多个歧义结果，必须立即停止发送流程并向用户澄清。
        5. **发送前校验**：调用发送工具前，必须在内部验证 `email` 格式合法且来源于上一步的工具输出。
        
        ## Available Tools
        - `query_agent_userinfo(user_name=None, department=None, user_id=None)`: 
          查询 agent_userinfo 表。支持按姓名模糊匹配、按部门精确匹配、按user_id精确匹配。
          ⚠️ 这是获取 email 和 user_name 的唯一合法途径。
        
        - `send_email(email: str, subject: str, content: str)`: 
          发送邮件。仅当 email 参数已通过上述工具验证后方可调用。确保 email 格式合法且来源于上一步的工具输出。
        ## Workflow
        请严格按照以下顺序执行，不可跳步：
        
        1. **意图解析**: 从用户请求中提取【收件人线索】(姓名/部门/user_id)、【主题关键词】、【正文要点】。
        2. **数据检索**: 使用提取的线索调用 `query_agent_userinfo`。
           - ✅ 若返回唯一记录 → 提取该记录的 user_name 和 email，进入步骤3
           - ❌ 若返回空 → 调用 ask_user_clarification 询问更具体的信息
           - ⚠️ 若返回多条 → 列出所有候选人的 user_name + department + email，让用户选择

    """
    summary_prompt = """
        任务:
            总结用户的对话，生成摘要，其中涉及用户信息的对话需要重点摘要
        规则:
            以第三人称的方式书写
        历史对话
            {messages}
    """
    memory_url = os.getenv('POSTGRESQL_URL')
    # 定义中间键
    summary = SummarizationMiddleware(
        model=model,
        trigger=('tokens', 30),
        keep=('messages', 3),
        summary_prompt=summary_prompt,
        trim_tokens_to_summarize=4000
    )
    # 创建智能体
    # 在异步函数中，有专门封装异步版的postgresaver
    async with AsyncPostgresSaver.from_conn_string(memory_url) as pg:
        # await pg.setup()
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
            middleware=[summary],
            checkpointer=pg
        )
        # 定义消息格式
        human_msg = {
            'messages': [
                HumanMessage(content=question)
            ]
        }
        config = {'configurable': {'thread_id': user_id}}
        # 获取结果
        rs = agent.astream_events(human_msg, config, verson='v2')
        async for event in rs:
            event_name = event['event']
            if event_name == 'on_chain_start':
                yield '\n正在理解用户意图...\n'
            elif event_name == 'on_chain_stream':
                yield '\n正在执行任务...\n'
                data = event['data']['chunk']
                if data:
                    if 'tools' in data:
                        content = data['tools']['messages'][0].content
                        if content:
                            yield content
                    elif 'model' in data:
                        content = data['model']['messages'][0].content
                        if content:
                            yield content


async def output(query, user_id):
    async for rs in personal_agent(query, user_id):
        print(rs, end='')
    return '执行成功'

if __name__ == '__main__':
    question1 = '通知cyx，明天上午来上课'
    question2 = '你好，我是cyx'
    question3 = '帮我写一个100字的数学加法课程 大纲'
    question4 = '请把课程大纲发送到我的邮箱里'
    question5 = '给张三发个邮件，让他记得吃午饭'
    # 当函数是个异步函数，就要用异步库中的函数来执行函数，即 asyncio.run()
    # 和postgresql建立连接要走I/O网络等待机制，Windows默认的实现机制和这个不兼容，所以需要指定一个兼容的实现机制
    asyncio.run(
        # output(question1, 1),
        # output(question2, 1),
        # output(question3, 1),
        output(question5, 1),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )


