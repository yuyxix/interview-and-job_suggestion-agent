import asyncio
import contextlib
import json
import time
from langgraph.checkpoint.memory import InMemorySaver
from app.ai.agent.multi_agent.node.question_node import question_node
from app.ai.agent.multi_agent.state.exam_state import ExamState
from app.ai.agent.multi_agent.node.intention_node import intention_node
from app.ai.agent.multi_agent.node.manager_node import manager_node
from app.ai.agent.multi_agent.node.answer_node import answer_node
from app.ai.agent.multi_agent.node.evaluate_node import evaluate_node
from app.ai.agent.multi_agent.node.chat_node import chat_node
from app.ai.agent.multi_agent.node.get_job_node import get_job_node
from app.ai.agent.multi_agent.memory.manage.memory_manager import MemoryManager, get_collection
from langgraph.graph import StateGraph, START
from langchain_core.messages import AIMessageChunk, HumanMessage
import uuid
"""
    模拟面试智能体画边,有高并发场景
"""


class ExamGraph:
    def __init__(self, checkpointer, redis):
        self.memory = checkpointer
        # 获取redis
        self.redis = redis
        # session_id -> 正在运行的图任务，用于切换/刷新时主动取消
        self._running = {}
        self.agent = self.get_graph()

    # 构件图
    def get_graph(self):
        graph = StateGraph(ExamState)
        # 添加节点
        graph.add_node('intention', intention_node)
        graph.add_node('question', question_node)
        graph.add_node('manager', manager_node)
        graph.add_node('answer', answer_node)
        graph.add_node('evaluate', evaluate_node)
        graph.add_node('chat', chat_node)
        graph.add_node('get_job', get_job_node)

        # 画边
        graph.add_edge(START, 'manager')
        graph.add_edge('intention', 'manager')
        graph.add_edge('question', 'manager')
        graph.add_edge('answer', 'manager')
        graph.add_edge('evaluate', 'manager')
        graph.add_edge('chat', 'manager')
        graph.add_edge('get_job', 'manager')
        # 编译
        self.agent = graph.compile(checkpointer=self.memory)
        return self.agent

    # 会话创建
    async def create_session(self, user_id) -> str:
        # 生成键名，用uuid，128位随机数，保证唯一性
        key = f'session'+uuid.uuid4().hex
        # 判断redis是否存在，兜底
        if self.redis:
            # 定义要存的数据，存入uuid与创建时间
            data = {'user_id': user_id, 'create_time': time.time()}
            # 存入
            await self.redis.set(key, json.dumps(data), ex=86400)
        return key

    # 检查会话: 会话id是否创建, 会话归属问题
    async def check_session(self, user_id, session_id):
        print('检查会话')
        if self.redis:
            # 获取会话数据
            data = await self.redis.get(session_id)
            # 检测会话是该用户创建的还是伪造的
            if not data:
                print('会话不存在')
                return False, '会话不存在'
            # 检查会话归属问题
            rs = json.loads(data)
            if rs['user_id'] != user_id:
                print('会话不属于该用户')
                return False, '会话不属于该用户'
            print('会话存在且归属用户')
            return True, '会话存在且归属用户'

    #  记忆存储
    async def memory_save(self, session_id, user_id, messages):
        mm = MemoryManager(session_id, user_id, collection=get_collection())
        return await mm.save_turn_async(messages, user_id, session_id)

    async def ensure_session(self, user_id, session_id):
        """校验会话；Redis 会话过期时自动重新登记

        侧边栏历史来自 Chroma，可能比 Redis 的 24 小时会话记录活得更久。
        用户点开旧会话继续聊时，不应该因为 Redis key 过期就报“会话不存在”。
        """
        ok, reason = await self.check_session(user_id, session_id)
        if ok:
            # 活跃会话续期，避免聊着聊着又过期
            try:
                await self.redis.expire(session_id, 86400)
            except Exception:
                pass
            return True, reason

        if reason == '会话不存在':
            await self.redis.set(
                session_id,
                json.dumps({'user_id': user_id, 'create_time': time.time()}),
                ex=86400,
            )
            print(f'Redis 会话已过期，重新登记: {session_id}')
            return True, '会话已重新登记'

        return False, reason

    async def chat(self, question, user_id, session_id):
        print(f'进入聊天：用户问题: {question}, 用户ID: {user_id}, 会话ID: {session_id}')
        # 1. 校验对话存在 + 归属匹配；过期但属于该用户的旧会话会自动重新登记
        ok, reason = await self.ensure_session(user_id, session_id)
        # 会话属于别人等无法恢复的情况，直接返回原因
        if not ok:
            yield reason
            return
        # 构建用户问题 —— 顺便把 user_id / memory_id 放进图状态，
        # 节点里（chat_node / evaluate_node）要靠它们去查记忆
        user_msg = {
            'messages': [HumanMessage(content=question)],
            'user_id': user_id,
            'memory_id': session_id,
        }
        # 配置检查点
        config = {'configurable': {'thread_id': session_id}}
        seen = set()  # 已经推过的"整条消息"的 id，用来去重
        collected = [{'role': 'user', 'content': question}]
        buffer = []
        current_node = None

        def flush_buffer():
            """节点切换 / 循环结束时，把攒到的文本落成一条 ai 消息"""
            if buffer:
                text = ''.join(buffer).strip()
                if text:
                    collected.append({'role': 'ai', 'content': text})
                buffer.clear()

        async with self._session_lock(session_id):
            async for mode, payload in self.agent.astream(
                user_msg, config, stream_mode=['messages', 'custom']
            ):
                if mode == 'messages':
                    chunk, meta = payload
                    # 这段文字是哪个节点产的；换节点 = 上一条消息结束
                    node = meta.get('langgraph_node')
                    if node != current_node:
                        flush_buffer()
                        current_node = node
                    if not chunk.content:
                        continue
                    if isinstance(chunk, AIMessageChunk):
                        if node not in ('chat', 'evaluate', 'get_job'):
                            continue
                        # 模型逐字输出的片段：同一条消息的所有片段共用一个 id，
                        # 这里绝不能去重，否则评价的流式输出会被压成一句
                        buffer.append(chunk.content)
                        yield chunk.content
                    elif chunk.id not in seen:
                        # 节点自己写的整条消息（意图识别成功/第N道题/答案已记录/评价完成…）
                        # 因为评价节点内部又开了一层流式，这些消息会被重复推送，按 id 去重
                        seen.add(chunk.id)

                        # chat 的正文已经通过 writer 的 custom 流逐字推给前端，
                        # 并且已经进了 buffer；这里只让 LangGraph 把它写进 state，
                        # 不再重复推送、也不重复写记忆。
                        if node == 'chat':
                            continue

                        buffer.append(chunk.content)
                        yield chunk.content
                else:
                    # custom 流推过来的是 writer() 里写的字典，例如
                    # {'type': 'evaluation', 'content': '...'}，不是消息对象
                    if isinstance(payload, dict) and payload.get('content'):
                        text = payload['content']
                        # 分隔线（\n\n---\n\n）是排版用的，别存进记忆；但还是要推给前端
                        if text.strip() and set(text.strip()) != {'-'}:
                            buffer.append(text)
                        yield text
            # 循环结束，最后一段别忘了落
            flush_buffer()

        # 记忆写入放在锁【外面】：摘要/画像要调模型（几秒），
        try:
            await self.memory_save(session_id, user_id, collected)
        except Exception as e:
            # 记忆坏了不该让这一轮失败 —— 回答早就推完了，
            # 这里抛出去的话路由的 except 会给前端发"流式异常"
            print(f'记忆保存失败: {type(e).__name__}: {e}')

    def register_session_task(self, session_id: str, task):
        self._running[session_id] = task

    def unregister_session_task(self, session_id: str, task):
        # 只有当前登记的确实是这个 task 才删，避免误删新请求的任务
        if self._running.get(session_id) is task:
            self._running.pop(session_id, None)

    async def cancel_session_task(self, session_id: str):
        """取消某个会话正在跑的图任务，并释放会话锁

        页面刷新、切换会话、退出登录时由前端调用；同会话新请求进来时
        也会先调用一次，避免旧任务一直占着锁。
        """
        task = self._running.pop(session_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=2)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
        await self.force_release_session_lock(session_id)

    async def force_release_session_lock(self, session_id: str):
        try:
            await self.redis.delete(f'session_lock:{session_id}')
        except Exception as e:
            print(f'强制释放会话锁失败: {type(e).__name__}: {e}')

    """
        会话锁：同一个sessin 同一时刻只允许一个请求进入
    """
    @contextlib.asynccontextmanager
    async def _session_lock(self, session_id: str):
        key = f'session_lock:{session_id}'
        # 生成随机token
        token = uuid.uuid4().hex
        # 尝试获取锁，px=60*1000表示过期时间，单位是毫秒
        # nx=True是Redis SET命令的一个选项，意思是：只有当这个key不存在时，才设置key的值
        #
        # 上一轮可能刚被取消，锁释放有一点点延迟；最多等 5 秒再报忙，
        # 避免用户切换回来立刻发消息时，被一个马上就会消失的锁挡住。
        deadline = time.monotonic() + 5
        while True:
            ok = await self.redis.set(key, token, px=60 * 1000, nx=True)
            if ok:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError('会话忙，请稍后再试')
            await asyncio.sleep(0.2)

        try:
            # yield的地方就是就是"锁内要执行的所有代码"插入的地方。
            yield
        finally:
            # 兜底处理，确保锁一定能释放
            # 释放锁，使用 Lua 脚本确保原子性，防止误删，误释放
            lua = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """
            try:
                # 执行 Lua 脚本，释放锁
                await self.redis.eval(lua, 1, key, token)
            except Exception:
                pass

    def draw(self):
        data = self.agent.get_graph().draw_mermaid_png()
        with open('出题图.png', 'wb') as f:
            f.write(data)
            print('打印成功')


if __name__ == '__main__':
    q1 = '给我一道python题'
    memory = InMemorySaver()
    agent = ExamGraph(memory)

    agent.draw()
    # async def test():
    #     async for c in agent.chat(q1, '1', '001'):
    #         print(c, end='')
    # asyncio.run(test())