from memory.save.long_memory import LongMemory
from memory.save.window_memory import WindowsMemory
from memory.save.summary_memory import SummaryMemory
from memory.save.profile_memory import ProfileMemory


class PromptBuilder:
    def __init__(self, session_id, user_id):
        self.windows_memory = WindowsMemory(session_id)
        self.summary_memory = SummaryMemory(session_id)
        self.long_memory = LongMemory()
        self.profile_memory = ProfileMemory(user_id)

    # 构建提示词
    def build_prompt(self, user_id, question):
        prompt = """
            一. 你是一个记忆提取助手
            二. 任务：
                - 理解用户需求
                - 根据用户问题，提取相关记忆
        """
        # 查询窗口记忆
        windows_memory = self.windows_memory.query()
        prompt += '短期记忆-窗口记忆'
        for i in windows_memory:
            if i['role'] == 'user':
                prompt += f'用户提问：{i["content"]}'
            else:
                prompt += f'AI回到：{i["content"]}'
        # 查询摘要记忆
        summary_memory = self.summary_memory.query()
        prompt += '短期记忆-摘要记忆'
        prompt += summary_memory
        # 查询长期记忆
        long_memory = self.long_memory.query(user_id, question)
        for item in long_memory:
            prompt += item + '\n'
        # 查询用户画像
        profile_memory = self.profile_memory.query()
        prompt += f'用户画像: {profile_memory}'
        return prompt

