from typing_extensions import TypedDict, Annotated
from langchain.messages import AnyMessage
import operator

"""
    邮件状态节点
"""


"""
    该类相当于定义了一个名为EmailState的字典类型，作为langgraph图的全局状态容器
    messages为其中一个键，用来存储对话
    list[AnyMessage]: 基础类型提示，表示该字段的值是一个包含 AnyMessage 对象的列表。
"""


class EmailState(TypedDict):
    # 消息列表，operator.add方法会自动往列表中添加新增的消息,而非覆盖消息
    # annotated类型注解,它允许在不改变类型本身的前提下，附加额外的元数据
    messages: Annotated[list[AnyMessage], operator.add]
    # 用户名
    name: str
    # 邮箱
    email: str
    # 主题
    subject: str
    # 内容
    content: str
    # 结果，可选,，可自定义返回给用户的内容
    result: str
    # 下一步操作,条件判断
    next_step: str