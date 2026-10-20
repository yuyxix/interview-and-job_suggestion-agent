
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from model.my_model import MyModel
from memory.save.profile_memory import ProfileMemory
from pydantic import BaseModel, Field


class ProfileParams(BaseModel):
    # 可以校验一些长期不可更改的信息
    name: str = Field(..., description='姓名')
    age: int = Field(..., description='年龄')
    job: str = Field(..., description='职业')
    address: str = Field(..., description='地址')
    degree: str = Field(..., description='学历')


"""
    长期记忆摘要智能体
"""


class ProfileAgent:
    def __init__(self, profile_memory: ProfileMemory):
        self.model = MyModel.get_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
        # 获取摘要记录保存对象
        self.profile_memory = profile_memory

    def get_prompt(self):
        self.prompt = """
            角色设定
                你是一个专业的用户画像结构化提取引擎。你的唯一任务是从非结构化的对话文本、行为日志或反馈记录中，精准提炼出高价值的用户特征标签，为下游的个性化推荐、长期记忆存储及AI人设适配提供标准化数据支撑。
            核心提取维度
                请严格围绕以下六个维度进行信息抽取，若原文未提及则标记为“未提及”，禁止推测或补全：
                    基础属性：姓名/昵称、年龄段、职业、所在地域、设备偏好等客观事实。
                    兴趣偏好：明确表达喜欢/讨厌的事物、高频讨论话题、内容消费倾向、审美风格。
                    技能与能力：掌握的专业技能、工具使用熟练度、语言能力、创作或工作能力边界。
                    长期计划与目标：职业规划、学习计划、生活目标、阶段性任务、待办事项。
                    交互风格偏好：喜欢的沟通语气（如简洁/详细、幽默/严肃）、回复长度、主动/被动倾向、敏感话题禁区。
                    关键事实与决策：已确认的个人重要信息、历史选择、价值观倾向、不可变更的约束条件。
                    处理规则
                    客观优先：仅提取原文中明确陈述或可强推断的信息，忽略情绪宣泄、寒暄、重复确认等无效内容。
                    第三人称表述：所有输出必须使用“用户”作为主语，严禁出现“我”“你”等人称代词。
                    去重与合并：相同维度的信息需整合为一条，避免碎片化；冲突信息以最新时间戳的内容为准。
                    隐私脱敏：自动过滤身份证号、银行卡号、精确住址等敏感隐私，仅保留可用于画像的泛化信息。
                    置信度标注：对模糊或间接推断的信息添加[低置信度]标签，明确区分事实与推测。
                输出限制：
                若没有明确的用户画像信息，直接返回空
                试例:
                    用户输入：我喜欢打游戏
                    输出：{'name': '', 'age': '', 'address': '', 'job': '', 'degree': ''}
                    用户输入：我是张三
                    输出：{'name': '张三', 'age': '0', 'address': '', 'job': '', 'degree': ''}
        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            response_format=ProfileParams,
            debug=True
        )
        return self.agent

    # 记忆更新
    # messages 窗口记忆的消息
    def update(self, user_id, question):
        # 提问
        human_msg = {'messages': [HumanMessage(content=question)]}
        rs = self.agent.invoke(human_msg)
        data = rs['structured_response'].model_dump()
        print(data)
        for key, value in data.items():
            if value:
                print('由用户画像')
                print(f'{key}: {value}')
                self.profile_memory.save(user_id, {key: value})


if __name__ == '__main__':
    long_memory_ob = ProfileMemory(1)
    long_memory_agent = ProfileAgent(long_memory_ob)
    question1 = '我喜欢打游戏'
    question2 = '我擅长编程'
    question3 = '我叫张三'
    long_memory_agent.update(1, question3)