from memory.retrieval.SummaryAgent import SummaryAgent
from memory.manage.session_manage import SessionManage
from memory.retrieval.long_memory_agent import LongMemoryAgent
from memory.retrieval.profile_agent import ProfileAgent
"""
    记忆管理器。管理记忆的更新
"""


class MemoryManager:
    def __init__(self, session_manage: SessionManage):
        # 摘要智能体
        self.summary_agent = SummaryAgent(session_manage.summary_memory)
        # 获取窗口记忆对象
        self.window_memory = session_manage.windows_memory
        # 创建长期记忆智能体
        self.long_agent = LongMemoryAgent(session_manage.long_memory)
        self.profile_agent = ProfileAgent(session_manage.profile_memory)

    def update(self, user_id, question):
        # 获取查询的窗口记忆
        query_windows = self.window_memory.query()
        # 更新长期记忆
        self.long_agent.update(user_id, question)
        self.profile_agent.update(user_id, question)
        if len(query_windows) >= 2:
            self.summary_agent.update(query_windows)
