from langchain.agents import create_agent
from app.ai.prompt.prompt_builder import BuilderPromptYaml
from app.ai.model.my_model import MyModel
from app.ai.agent.multi_agent.memory.save.profile_memory import ProfileMemory


"""
    用户画像更新智能体

    输出一份完整的纯文本画像（不再是固定的结构化字段）：
    画像按用户只存一份，每次用「旧画像 + 最近 20 轮总结」整体重写。
"""


class ProfileAgent:
    def __init__(self, profile_memory: ProfileMemory):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
        # 获取摘要记录保存对象
        self.profile_memory = profile_memory

    def get_prompt(self):
        self.prompt = BuilderPromptYaml.get_prompt('profile_agent.yaml')
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
        )
        return self.agent

