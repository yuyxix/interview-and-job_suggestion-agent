from typing_extensions import TypedDict, Annotated
from langchain.messages import AnyMessage
import operator


# 定义消息状态
class EmailState(TypedDict):
    # 定义消息形式
    messages: Annotated[list[AnyMessage], operator.add]
    # 用户名
    name: str
    # 邮箱
    email: str
    # 主题
    subject: str
    # 内容
    content: str
    # 结果形式，可选
    result: str
    # 下一步操作,条件判断
    next_step: str
    # 意图标识
    flag: str
    # 置信度
    confidence: float