from fastapi import APIRouter

from chat.service import HistoryService

history_router = APIRouter()

@history_router.get(
    path='/queryHistoryMenu',
    summary='查询历史菜单',
)
def query_history_menu(username:  str):
    return HistoryService.query_history_menu(username)

@history_router.get(
    path='/conversationLog',
    summary='查询某条详细对话记录',
)
def conversation_log(historyId: int):
    return HistoryService.conversation_log(historyId)