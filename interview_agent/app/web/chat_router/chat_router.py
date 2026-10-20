from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.ai.agent.multi_agent.memory.manage.memory_manager import MemoryManager
from app.ai.agent.vosk_agent import VoskAgent
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from pydantic import BaseModel
chat_router = APIRouter()
vosk_router = APIRouter()
history_router = APIRouter()
profile_router = APIRouter()
# 语音实例按需加载（第一次连接 WebSocket 时加载模型）


class SessionSchema(BaseModel):
    session_id: str = None
    user_id: str = None


class ProfileSchema(BaseModel):
    user_id: str = ''
    profile: str = ''


@chat_router.post('/create_session')
async def create_session(request: Request, session: SessionSchema):
    print(f'用户ID: {session.user_id} 会话ID: {session.session_id}')
    exam_agent = request.app.state.exam_agent
    # 前端返回数据若没有session_id，直接建新的
    # 这一步必须放在查 redis 之前 —— 否则会拿 None 当 key 去查
    if not session.session_id:
        new_session_id = await exam_agent.create_session(session.user_id)
        return {
            'code': 200,
            'message': '新建会话创建成功',
            "data": {'session_id': new_session_id}
        }
    # 带了 session_id 才去校验它存不存在、是不是这个用户的
    # 参数顺序要和 check_session(self, user_id, session_id) 一致，传反了会永远判成"会话不存在"
    is_exist, msg = await exam_agent.check_session(session.user_id, session.session_id)
    if not is_exist:
        print('会话不存在！创建新会话')
        session_id = await exam_agent.create_session(session.user_id)
        print(f'新会话id: {session_id}')
        return {
            'code': 200,
            'message': '会话不存在，会话新创建成功',
            "data": {'session_id': session_id}
        }
    else:
        print('会话存在')
        return {
            'code': 200,
            'message': '会话存在',
            "data": {'session_id': session.session_id}
        }


# 聊天接口
@chat_router.get("/chat")
async def chat(request: Request, question: str, user_id: str, session_id: str):
    print(f'用户问题: {question}, 用户ID: {user_id}, 会话ID: {session_id}')
    # 通过request的api获取到加载好的exam_agent对象
    exam_agent = request.app.state.exam_agent

    async def generate():
        # 同会话新请求进来时，先把上一轮可能还在跑的任务取消掉并释放锁。
        # 这样即使前端没来得及发 cancel 通知，也不会撞“会话忙”。
        await exam_agent.cancel_session_task(session_id)

        # 图任务放到后台，前台负责转发 SSE，并定时检查客户端是否还连着。
        # 用户切换会话/刷新页面时 SSE 会断开，这里要主动取消图任务，
        # 否则它会继续占着 session_lock 直到 60 秒 TTL 过期。
        queue = asyncio.Queue()

        async def producer():
            try:
                async for chunk in exam_agent.chat(question, user_id, session_id):
                    await queue.put(('chunk', chunk))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                await queue.put(('error', e))
            finally:
                await queue.put(('done', None))

        task = asyncio.create_task(producer())
        exam_agent.register_session_task(session_id, task)
        try:
            while True:
                try:
                    kind, value = await asyncio.wait_for(queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    if await request.is_disconnected():
                        print('客户端已断开，取消本轮对话并释放会话锁')
                        break
                    continue

                if kind == 'chunk':
                    data = {'data': value, 'Done': False}
                    yield f'data: {json.dumps(data, ensure_ascii=False)}\n\n'
                elif kind == 'error':
                    print(value)
                    data = {'data': '流式异常', 'done': True}
                    yield f'data: {json.dumps(data, ensure_ascii=False)}\n\n'
                    break
                else:  # done
                    data = {'data': '', 'done': True}
                    yield f'data: {json.dumps(data, ensure_ascii=False)}\n\n'
                    break
        finally:
            exam_agent.unregister_session_task(session_id, task)
            # 取消图任务：会触发 exam_agent.chat 里的 async with，
            # 在 finally 中执行 Lua 删除 session_lock。
            if not task.done():
                task.cancel()
            try:
                await asyncio.wait_for(task, timeout=3)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
            # 极端情况下图任务没在 3 秒内退出（例如底层模型调用卡住），
            # 强制释放锁，避免用户切换回来/刷新后被锁 60 秒。
            if not task.done():
                print('图任务取消超时，强制释放会话锁')
                await exam_agent.force_release_session_lock(session_id)

    # 返回的结果，默认是ajax
    return StreamingResponse(generate(), media_type='text/event-stream')


@chat_router.post('/chat/cancel')
async def cancel_chat(request: Request, user_id: str = None, session_id: str = None):
    """前端刷新/切换会话时主动取消当前会话任务并释放锁

    使用 sendBeacon 调用，必须是 POST，参数放在 query 上。
    """
    if not session_id:
        return {'code': 400, 'msg': '缺少 session_id', 'data': None}
    exam_agent = request.app.state.exam_agent
    try:
        await exam_agent.cancel_session_task(session_id)
        return {'code': 200, 'msg': '已取消当前会话任务', 'data': None}
    except Exception as e:
        return {'code': 500, 'msg': f'取消失败:{e}', 'data': None}


@history_router.get("/history/session")
async def get_session_history(request: Request, user_id: str, memory_id: str):
    mm = MemoryManager(memory_id, user_id, collection=request.app.state.collection)
    try:
        messages = await asyncio.to_thread(mm.load_messages, user_id, memory_id)
        return {'code': 200, 'msg': '获取成功', 'data': messages}
    except Exception as e:
        return {'code': 500, 'msg': f'获取历史失败:{e}', 'data': None}


@history_router.get("/get_history")
async def get_history(request: Request, user_id: str, session_id: str = None):
    def _load():
        # 注意：查"所有会话"时不要给构造器传空字符串 ——
        # 记忆管理器会校验 id 非空（空值会让所有人的记忆混在一起）
        mm = MemoryManager(session_id, user_id, collection=request.app.state.collection)
        if session_id:
            return mm.load_messages(user_id, session_id)
        return mm.load_user_messages(user_id, with_memory_id=True)

    try:
        data = await asyncio.to_thread(_load)
        return {'code': 200, 'msg': '获取成功', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': f'获取历史失败:{e}', 'data': None}


@history_router.get("/history/search")
async def search_history(request: Request, user_id: str, keyword: str,
                         memory_id: str):
    def _search():
        mm = MemoryManager(memory_id, user_id, collection=request.app.state.collection)
        return mm.search_memory(keyword, user_id, memory_id)

    try:
        matches = await asyncio.to_thread(_search)
    except Exception as e:
        return {'code': 500, 'msg': f'搜索失败:{e}', 'data': None}

    return {
        'code': 200,
        'msg': f'命中 {len(matches)} 条' if matches else '没有找到相关记忆',
        'data': {'total': len(matches), 'keyword': keyword, 'matches': matches},
    }


@history_router.delete("/history/session")
async def delete_session_history(request: Request, user_id: str, memory_id: str):
    def _delete():
        mm = MemoryManager(memory_id, user_id, collection=request.app.state.collection)
        detail = {}

        # 1) 长期记忆（Chroma）
        try:
            detail['long'] = mm.long.delete(user_id, memory_id)
        except Exception as e:
            detail['long_error'] = f'{type(e).__name__}: {e}'

        # 2) 窗口记忆 + 轮次计数（Redis）
        try:
            keys = [f'windows_memory:{user_id}:{memory_id}',
                    f'memory_turn:{user_id}:{memory_id}']
            detail['redis_deleted'] = mm.windows.redis.delete(*keys)
        except Exception as e:
            detail['redis_error'] = f'{type(e).__name__}: {e}'

        # 3) 摘要（PG）
        try:
            mm.summary.delete()
            detail['summary_deleted'] = True
        except Exception as e:
            detail['summary_error'] = f'{type(e).__name__}: {e}'

        return detail

    try:
        detail = await asyncio.to_thread(_delete)
    except Exception as e:
        return {'code': 500, 'msg': f'删除失败:{e}', 'data': None}

    # 4) 图的多轮状态（checkpointer 那条线程）—— 不清的话，下次进这个会话还能接着跑
    try:
        await request.app.state.exam_agent.memory.adelete_thread(memory_id)
        detail['checkpoint_deleted'] = True
    except Exception as e:
        detail['checkpoint_error'] = f'{type(e).__name__}: {e}'

    return {'code': 200, 'msg': '会话历史已删除', 'data': detail}


@history_router.delete("/history/message")
async def delete_message(request: Request, user_id: str, memory_id: str,
                         document_id: str = None, keyword: str = None):
    if not document_id and not keyword:
        return {'code': 400, 'msg': '需要 document_id 或 keyword 才能定位到某一条', 'data': None}

    def _delete():
        mm = MemoryManager(memory_id, user_id, collection=request.app.state.collection)

        if document_id:
            target_id = document_id
        else:
            matches = mm.search_memory(keyword, user_id, memory_id)
            if not matches:
                return {'code': 404, 'msg': '没有匹配到记录', 'data': None}
            if len(matches) > 1:
                return {'code': 409,
                        'msg': f'匹配到 {len(matches)} 条，请用 document_id 指定要删哪一条',
                        'data': {'matches': matches}}
            target_id = matches[0]['document_id']

        mm.collection.delete(ids=[target_id])
        return {'code': 200, 'msg': '已删除该条记录', 'data': {'document_id': target_id}}

    try:
        return await asyncio.to_thread(_delete)
    except Exception as e:
        return {'code': 500, 'msg': f'删除失败:{e}', 'data': None}


# ==================== 用户画像 ====================
@profile_router.get('/profile')
async def get_user_profile(request: Request, user_id: str):
    """查看该用户的画像（前端"我的画像"弹窗用）

    画像按 user_id 存、跨会话共用，所以不需要 memory_id。
    """
    uid = (user_id or '').strip()
    if not uid:
        return {'code': 400, 'msg': '缺少 user_id', 'data': None}

    def _load():
        mm = MemoryManager(None, uid, collection=request.app.state.collection)
        return mm.load_profile(uid)

    try:
        profile = await asyncio.to_thread(_load)
        return {'code': 200, 'msg': '获取成功', 'data': {'profile': profile or ''}}
    except Exception as e:
        return {'code': 500, 'msg': f'获取画像失败:{e}', 'data': None}


@profile_router.put('/profile')
async def update_user_profile(request: Request, body: ProfileSchema):
    uid = (body.user_id or '').strip()
    if not uid:
        return {'code': 400, 'msg': '缺少 user_id', 'data': None}
    if len(body.profile or '') > 5000:
        return {'code': 400, 'msg': '画像不能超过 5000 字', 'data': None}

    def _save():
        mm = MemoryManager(None, uid, collection=request.app.state.collection)
        return mm.save_profile(body.profile or '', uid)

    try:
        profile = await asyncio.to_thread(_save)
        return {'code': 200, 'msg': '画像已保存', 'data': {'profile': profile or ''}}
    except Exception as e:
        return {'code': 500, 'msg': f'保存画像失败:{e}', 'data': None}


# 语音输入
@vosk_router.websocket('/vosk')
async def vosk(ws: WebSocket):
    await ws.accept()
    try:
        # 模型加载放到线程里，避免第一次连接时卡住事件循环
        agent = await asyncio.to_thread(VoskAgent.get_vosk)
        await agent.vosk_chat(ws, accepted=True)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f'语音识别连接异常: {type(e).__name__}: {e}')
        try:
            await ws.close()
        except Exception:
            pass