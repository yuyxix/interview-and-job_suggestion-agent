from memory.save.window_memory import WindowsMemory
from memory.save.summary_memory import SummaryMemory
from memory.save.long_memory import LongMemory
from memory.manage.prompt_builder import PromptBuilder
from memory.save.profile_memory import ProfileMemory
"""
    会话管理器：主要负责四层记忆的对象创建和提示词生成
"""


class SessionManage:
    def __init__(self, session_id: str, user_id):
        self.session_id = session_id
        self.windows_memory = WindowsMemory(session_id)
        self.prompt_builder = PromptBuilder(self.session_id, user_id)
        self.summary_memory = SummaryMemory(session_id)
        self.long_memory = LongMemory()
        self.profile_memory = ProfileMemory(user_id)

    # 添加窗口记忆
    def save(self, role: str, content: str):
        self.windows_memory.save(role, content)

    # 构建提示词
    def build_prompt(self, user_id, question):
        prompt = self.prompt_builder.build_prompt(user_id, question)
        return {'role': 'system', 'content': prompt}
