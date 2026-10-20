from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from model.my_model import MyModel
from memory.save.summary_memory import SummaryMemory

"""
    摘要智能体
"""


class SummaryAgent:
    def __init__(self, summary_memory: SummaryMemory):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
        # 获取摘要记录保存对象
        self.summary_memory = summary_memory

    def get_prompt(self):
        self.prompt = """
            角色：
                你是一个对话记忆摘要助手。
            任务：
                根据就摘要和聊天记录生成新摘要
            请严格遵循以下规则处理输入内容：
                内容筛选：仅提取与任务、需求、事实、决策及用户明确提供的个人信息相关的关键内容，完全忽略寒暄、情绪表达、重复确认等闲聊信息。
                叙述规范：全程使用第三人称（如“用户”“该用户”），禁止出现“我”“你”等第一、二人称代词。
                信息优先级：优先保留用户的姓名、身份、偏好、历史行为、明确诉求等个人信息，确保关键用户画像不丢失。
                格式约束：摘要字数严格控制在200字以内，仅输出摘要正文，禁止添加任何解释、标题、标点修饰或无关说明。
                匹配规则：若输入全为闲聊内容，直接摘要某个用户和你对话的大概内容。
                输出内容：只输出新摘要
        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=[]
        )
        return self.agent

    # 记忆更新
    # messages 窗口记忆的消息
    def update(self, messages):
        # 查询旧摘要
        old_summary_memory = self.summary_memory.query()
        # 拼接新的聊天记录
        prompt = ''
        for i in messages:
            if i['role'] == 'user':
                prompt += f'用户提问"{i['content']}'
            elif i['role'] == 'ai':
                prompt += f'AI回答: {i['content']}'
        # 拼接最新的聊天记录
        question = f'请根据旧摘要: {old_summary_memory}和最新聊天记录{prompt}'
        # 提问
        human_msg = {'messages': [HumanMessage(content=question)]}
        rs = self.agent.invoke(human_msg)
        # 把新摘要存入到摘要记忆中
        self.summary_memory.save(rs['messages'][-1].content)


if __name__ == '__main__':
    sm = SummaryMemory('002')
    s = SummaryAgent(sm)
    record = [
                {"role": "user", "content": "你好，我叫林悦，是一名UI设计师"},
                {"role": "ai", "content": "你好林悦，很高兴认识你，有什么可以帮你的吗"},
                {"role": "user", "content": "我最近在做一款健身App的设计，偏好极简风格"},
                {"role": "ai", "content": "收到，已记录你的项目方向和设计风格偏好"},
                {"role": "user", "content": "对了，我对深色模式有执念，希望默认就是暗色主题"},
                {"role": "ai", "content": "明白，已将暗色主题作为默认设计需求纳入记忆"},
            ]
    s.update(record)