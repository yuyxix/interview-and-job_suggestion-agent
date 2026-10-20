from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from app.ai.model.my_model import MyModel
from app.ai.agent.multi_agent.memory.save.summary_memory import SummaryMemory
from app.ai.prompt.prompt_builder import BuilderPromptYaml
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
        self.prompt = BuilderPromptYaml.get_prompt('summary_agent.yaml')

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
        )
        return self.agent
