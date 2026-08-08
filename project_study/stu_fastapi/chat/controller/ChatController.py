import json
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse
from chat.service import ChatService
from chat.entity.ConversationResultEntity import ConversationEntity, DeleteConversationEntity

chat_router = APIRouter()

@chat_router.get(
    path='/chat',
    summary='聊天',
    description="""
            聊天
            访问路径：http://localhost:8000/chat/chat
            请求参数；
                question: 用户问题
            返回值：
                流式输出 sse
        """
)
def chat(question: str, historyId: int):
    # 流式处理
    def generator():
        for chunk in ChatService.chat(question, historyId):
            yield f'data: {json.dumps({'content': chunk})}\n\n'
        yield f'data: {json.dumps({'content': '[DONE]'})}\n\n'
    return StreamingResponse(
        content=generator(),
        media_type='text/event-stream'
    )

@chat_router.post(
    path='/saveConversationResult',
    summary='保存对话结果',
    description='''
        保存会话结果
        访问路径: http://localhost:8000/chat/saveConversationResult
    '''
)
def save_conversation_result(conversationResult: ConversationEntity):
    username = conversationResult.username
    question = conversationResult.question
    parent_id = conversationResult.parentId
    answer = conversationResult.answer
    return ChatService.save_conversation_result(conversationResult)

@chat_router.post(
    path='/deleteConversationHistory',
    summary='删除对话记录',
    description='''
        删除会话记录
        访问路径: http://localhost:8000/chat/deleteConversationHistory
    '''
)
def delete_conversation_history(deleteHistory: DeleteConversationEntity):
    historyId = deleteHistory.historyId
    print('我执行了')
    return ChatService.delete_conversation_history(historyId)