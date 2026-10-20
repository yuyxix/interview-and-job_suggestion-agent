import operator

from typing_extensions import TypedDict, Annotated
from langchain.messages import AnyMessage


'''
    考试节点状态
'''


class ExamState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    # 【意图识别节点】
    # 课程
    course: str
    # 题目数量
    total: int
    # 【出题节点】
    # 题目列表
    question: list[dict[str, any]]
    # 当前的题目
    current_question: str
    # 【收集用户的答案】
    # 用户的答案列表
    user_answer: list[dict[str, any]]
    # 【控制出题节奏】
    # 当前答题题目索引
    current_index: int
    # 【评价节点】
    # 评价结果
    evaluation: str
    # 当前状态
    exam_step: str
    # 当前题目的编号
    question_id: int
    # 是否继续出题
    continue_question: bool
    # 标准答案
    sure_answer: list[dict[str, any]]
    # 记忆隔离
    user_id: str
    memory_id: str
