
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from model.my_model import MyModel
from memory.save.long_memory import LongMemory

"""
    长期记忆摘要智能体
"""


class LongMemoryAgent:
    def __init__(self, long_memory: LongMemory):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
        # 获取摘要记录保存对象
        self.long_memory = long_memory

    def get_prompt(self):
        self.prompt = """
            角色：长期记忆摘要助手。
            任务：根据旧摘要与聊天记录生成新摘要。
            规则：
                仅提取用户个人信息（姓名、身份、喜好、兴趣、技能、长期计划、明确诉求）、关键事实与决策，
            忽略寒暄情绪及重复确认。全程使用第三人称“用户”，禁用第一二人称。优先保留并更新用户画像要素，
            确保偏好与计划不丢失。若全为闲聊则简述对话主题。字数严格控制在200字以内，仅输出摘要正文，
            无标题解释或额外修饰。
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
    def update(self, user_id, question):
        # 提问
        human_msg = {'messages': [HumanMessage(content=question)]}
        rs = self.agent.invoke(human_msg)
        # 把新摘要存入到摘要记忆中
        self.long_memory.save(user_id, rs['messages'][-1].content)
        print('长期记忆更新成功')


if __name__ == '__main__':
    long_memory_ob = LongMemory()
    long_memory_agent = LongMemoryAgent(long_memory_ob)
    question1 = '我喜欢打游戏'
    question2 = '我擅长编程'
    long_memory_agent.update(1, question1)