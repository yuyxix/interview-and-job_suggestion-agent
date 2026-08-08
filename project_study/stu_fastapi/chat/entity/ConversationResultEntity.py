from pydantic import BaseModel, Field


class ConversationEntity(BaseModel):
    username: str = Field(..., description="用户名")
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="答案")
    parentId: int = Field(..., description="父级id")

class DeleteConversationEntity(BaseModel):
    historyId: int = Field(..., description="历史记录id")