
import asyncio

from langchain_core.messages import HumanMessage

from app.ai.agent.multi_agent.memory.save.long_memory import LongMemory
from app.ai.agent.multi_agent.memory.save.profile_memory import ProfileMemory
from app.ai.agent.multi_agent.memory.save.summary_memory import SummaryMemory
from app.ai.agent.multi_agent.memory.save.windows_memory import WindowsMemory

# 向量库注册位：在 main.py 的 lifespan 里 set_collection(app.state.collection)
_runtime_collection = None


def set_collection(collection) -> None:
    global _runtime_collection
    _runtime_collection = collection


def get_collection():
    if _runtime_collection is None:
        raise RuntimeError(
            '向量库还没注册：请在 main.py 的 lifespan 里加一行 '
            'memory_manager.set_collection(app.state.collection)'
        )
    return _runtime_collection


def _wrap_long_memory(collection) -> LongMemory:

    memory = LongMemory.__new__(LongMemory)
    memory.collection = collection
    return memory


def _role_of(raw) -> str:

    r = str(raw or '').lower()
    if 'human' in r or r == 'user':
        return 'user'
    if 'ai' in r:
        return 'ai'
    return r or 'user'


# 将记忆格式标准化
def normalize_messages(messages) -> list:

    if messages is None:
        return []
    if isinstance(messages, (str, dict)) or hasattr(messages, 'content'):
        messages = [messages]

    pairs = []
    for m in messages:
        if isinstance(m, str):
            role, content = 'user', m
        elif isinstance(m, dict):
            role = m.get('role') or m.get('type') or 'user'
            content = m.get('content') or ''
        else:
            role = getattr(m, 'type', 'user')
            content = getattr(m, 'content', '')
        content = content if isinstance(content, str) else str(content)
        if content.strip():
            pairs.append((_role_of(role), content))
    return pairs


# 总记忆管理器
class MemoryManager:

    def __init__(self, memory_id=None, user_id=None, collection=None,
                 summary_every: int = 5, profile_every: int = 20):
        self.memory_id = memory_id
        self.user_id = user_id
        self.collection = collection if collection is not None else get_collection()
        self.summary_every = summary_every
        self.profile_every = profile_every

        self.windows = None
        self.summary = None
        self.profile = None
        self.long = None
        self._turn_key = None
        self._bound = None          # 当前绑的是哪个 (user_id, memory_id)

        # 两个 retriever 智能体：懒加载（create_agent 有开销，用不到就不建）
        self._profile_agent = None
        self._summary_agent = None

        if memory_id is not None and user_id is not None:
            self._bind(self.user_id, self.memory_id)

    # 绑定：确认这次操作的是"谁的、哪一段"记忆
    def _bind(self, user_id=None, memory_id=None):
        if user_id is not None and not str(user_id).strip():
            raise ValueError(f'user_id 传了空值：{user_id!r}（不知道是谁的记忆，拒绝执行）')
        if memory_id is not None and not str(memory_id).strip():
            raise ValueError(f'memory_id 传了空值：{memory_id!r}（不知道是哪段记忆，拒绝执行）')

        uid = str(user_id if user_id is not None else (self.user_id or '')).strip()
        mid = str(memory_id if memory_id is not None else (self.memory_id or '')).strip()
        if not uid or not mid:
            raise ValueError(
                f'缺少 user_id / memory_id（当前 user_id={uid!r}, memory_id={mid!r}）。'
                f'空值会让不同用户共用同一份记忆，所以这里直接拒绝：'
                f'要么构造 MemoryManager 时传，要么每次调用时传'
            )
        if self._bound == (uid, mid):
            return
        self.user_id, self.memory_id = uid, mid
        self.windows = WindowsMemory(mid, uid)          # 四层自己的参数名叫 session_id
        self.summary = SummaryMemory(mid, uid)
        self.profile = ProfileMemory(uid)
        self.long = _wrap_long_memory(self.collection)
        # 摘要轮次按会话计；画像轮次按用户计（画像跨会话共用，换会话不该从 0 重新数）
        self._turn_key = f'memory_turn:{uid}:{mid}'
        self._profile_turn_key = f'profile_turn:{uid}'
        self._bound = (uid, mid)
        # 换了用户，两个智能体也得跟着换（它们持有对应的 memory 对象）
        self._profile_agent = None
        self._summary_agent = None

    # 一、存：传 messages
    # 保存每一轮对话，窗口对话与长期对话会用到
    def save_turn(self, messages, user_id: str = None, memory_id: str = None) -> dict:
        self._bind(user_id, memory_id)
        pairs = normalize_messages(messages)
        if not pairs:
            return {'saved': 0, 'msg': 'messages 为空，没存任何东西'}

        result = {'saved': 0, 'turns': []}

        # 逐条落库：窗口记忆（只留最近 N 条）+ 长期记忆（完整原文，前端要取回）
        for role, content in pairs:
            try:
                self.windows.save(role, content)
            except Exception as e:
                result['windows_error'] = f'{type(e).__name__}: {e}'
            try:
                self.long.save(self.memory_id, self.user_id, f'{role}: {content}')
            except Exception as e:
                result['long_error'] = f'{type(e).__name__}: {e}'
            result['saved'] += 1

        # 轮次：这批里有几条用户发言就推进几轮（一问一答算一轮）
        user_count = sum(1 for role, _ in pairs if role == 'user')
        try:
            for _ in range(user_count):
                result['turns'].append(self._next_turn())
        except Exception as e:
            result['turn_error'] = f'{type(e).__name__}: {e}'

        # 摘要：轮次跨过了 summary_every 的倍数就生成一次
        if self.summary_every and result['turns']:
            if any(t % self.summary_every == 0 for t in result['turns']):
                try:
                    result['summary'] = self.update_summary()
                except Exception as e:
                    result['summary_error'] = f'{type(e).__name__}: {e}'

        # 画像：按【用户】累计轮次，每 profile_every 轮更新一次。
        #    和摘要不同，这里不能用会话轮次 —— 换会话后计数不该从头开始，
        #    否则用户一直换会话就永远凑不满 20 轮。
        if self.profile_every and user_count:
            before, after = 0, 0
            try:
                before, after = self._next_profile_turns(user_count)
            except Exception as e:
                result['profile_turn_error'] = f'{type(e).__name__}: {e}'

            # 这批轮次是否跨过了 profile_every 的整数倍（19→21、20→20 都算）
            if after // self.profile_every > before // self.profile_every:
                try:
                    result['profile'] = self.update_profile()
                except Exception as e:
                    result['profile_error'] = f'{type(e).__name__}: {e}'

        return result

    async def save_turn_async(self, messages, user_id: str = None, memory_id: str = None) -> dict:
        """异步节点里用这个：把同步的四层读写丢到线程里，不阻塞事件循环"""
        return await asyncio.to_thread(self.save_turn, messages, user_id, memory_id)

    # 二、取：传 user_id + memory_id
    def load_messages(self, user_id: str = None, memory_id: str = None) -> list:
        """把这个会话存过的完整对话取回来

        形如 ['user: 帮我一道python题', 'ai: 第1道题: ...']。
        两个 id 都参与过滤 —— 不会取到别人的、也不会取到别的会话的。
        """
        self._bind(user_id, memory_id)
        return self.long.get_history(self.user_id, self.memory_id) or []

    def load_user_messages(self, user_id: str = None, with_memory_id: bool = False) -> list:
        # 这里不能走 _bind：那个是"会话级"的绑定，会要求 memory_id 非空；
        #   而"按用户跨会话"的查询天然不需要 memory_id
        uid = str(user_id if user_id is not None else (self.user_id or '')).strip()
        if not uid:
            raise ValueError('load_user_messages 需要 user_id（空值会取到所有人的记忆）')

        rs = self.collection.get(
            where={'user_id': uid},
            include=['documents', 'metadatas'],
        )
        documents = rs.get('documents') or []
        metadatas = rs.get('metadatas') or []
        ids = rs.get('ids') or []
        if not with_memory_id:
            return documents
        # document_id 给前端搜索结果里的"删除这一条"用
        return [
            {
                'content': doc,
                'memory_id': (meta or {}).get('session_id'),
                'document_id': ids[i] if i < len(ids) else None,
            }
            for i, (doc, meta) in enumerate(zip(documents, metadatas))
        ]

    def load_windows(self, user_id: str = None, memory_id: str = None) -> list | None:
        """最近几轮对话（窗口记忆）：[{'role':..,'content':..}, ...]"""
        self._bind(user_id, memory_id)
        return self.windows.query()

    def load_summary(self, user_id: str = None, memory_id: str = None) -> str:
        """这一段会话的摘要"""
        self._bind(user_id, memory_id)
        return self.summary.query()

    def load_summaries(self, user_id: str = None, memory_id: str = None,
                       limit: int = 2) -> list:
        """该用户最近的 N 条摘要（当前会话优先，其次其它会话）"""
        self._bind(user_id, memory_id)
        return self.summary.query_recent(limit) or []

    def load_profile(self, user_id: str = None, memory_id: str = None) -> str:
        uid = str(user_id if user_id is not None else (self.user_id or '')).strip()
        if memory_id is None and self.memory_id is None:
            if not uid:
                raise ValueError('画像读写需要 user_id（空值会取到所有人的画像）')
            return ProfileMemory(uid).query()
        self._bind(user_id, memory_id)
        return self.profile.query()

    def save_profile(self, profile: str, user_id: str = None) -> str:
        uid = str(user_id if user_id is not None else (self.user_id or '')).strip()
        if not uid:
            raise ValueError('画像写入需要 user_id（空值会让不同用户互相覆盖）')
        ProfileMemory(uid).save(profile)
        return profile

    # 旧名字保留，不破坏已有调用（chat_router 里的 /get_history 用的就是它们）
    def get_conversation(self, user_id: str = None, memory_id: str = None) -> list:
        return self.load_messages(user_id, memory_id)

    def get_user_history(self, user_id: str = None, with_memory_id: bool = False) -> list:
        return self.load_user_messages(user_id, with_memory_id)

    def get_windows(self): return self.load_windows()
    def get_summary(self): return self.load_summary()
    def get_profile(self): return self.load_profile()

    # 三、检索：传 question
    def recall(self, question: str, user_id: str = None, memory_id: str = None,
               n_results: int = 3, same_session_only: bool = False,
               exclude_session_id: str = None) -> list:
        self._bind(user_id, memory_id)
        scope = self.memory_id if same_session_only else None
        return self.long.query(
            self.user_id, question,
            session_id=scope,
            exclude_session_id=exclude_session_id,
            n_results=n_results,
        ) or []

    def search_memory(self, keyword: str, user_id: str = None,
                      memory_id: str = None) -> list:
        self._bind(user_id, memory_id)
        return self.long.search_memory(self.user_id, self.memory_id, keyword) or []

    def get_context(self, question: str = None, user_id: str = None,
                    memory_id: str = None, same_session_only: bool = False,
                    exclude_session_id: str = None,
                    window_messages: int = 3, summary_limit: int = 2,
                    recall_n: int = 2, max_chars: int = 3000) -> str:
        self._bind(user_id, memory_id)

        # 下面四块各自兜底：任何一块失败都只是少一块，不能让整段上下文消失
        try:
            profile = (self.load_profile() or '').strip()
        except Exception as e:
            print(f'[memory] 画像读取失败: {type(e).__name__}: {e}')
            profile = ''

        summaries = []
        if summary_limit:
            try:
                summaries = self.load_summaries(limit=summary_limit)
            except Exception as e:
                print(f'[memory] 摘要读取失败: {type(e).__name__}: {e}')

        recalled = []
        if question:
            try:
                recalled = self.recall(
                    question,
                    n_results=recall_n,
                    same_session_only=same_session_only,
                    exclude_session_id=exclude_session_id,
                )
            except Exception as e:
                print(f'[memory] 向量召回失败: {type(e).__name__}: {e}')

        try:
            windows = self.load_windows() or []
        except Exception as e:
            print(f'[memory] 窗口记忆读取失败: {type(e).__name__}: {e}')
            windows = []
        recent = windows[-window_messages:] if window_messages else []

        def compose(sums):
            parts = []
            if profile:
                parts.append('【用户画像】\n' + profile)

            for item in sums:
                summary = (item.get('summary') or '').strip()
                if not summary:
                    continue
                label = ('【本场摘要】'
                         if str(item.get('session_id')) == str(self.memory_id)
                         else '【历史会话摘要】')
                parts.append(label + summary)

            if recalled:
                parts.append(
                    '【相关历史记忆】\n'
                    + '\n'.join(f'- {str(r)}' for r in recalled)
                )

            if recent:
                lines = [f"{w.get('role')}: {w.get('content')}" for w in recent]
                parts.append('【最近对话】\n' + '\n'.join(lines))

            return '\n\n'.join(parts)

        text = compose(summaries)
        # 超长时降级：两条摘要只留一条（当前会话优先），其余不动
        if len(text) > max_chars and len(summaries) > 1:
            text = compose(summaries[:1])
        return text

    # 摘要 / 画像的生成（内部用，也可以手动触发）
    def update_summary(self) -> str:
        old = self.load_summary() or ''
        recent = self._recent_dialogue(self.summary_every)
        content = (f'已有摘要：\n{old}\n\n' if old else '') + f'最近的对话：\n{recent}'

        rs = self._get_summary_agent().agent.invoke(
            {'messages': [HumanMessage(content=content)]}
        )
        text = rs['messages'][-1].content
        self.summary.save(text)
        return text

    def update_profile(self) -> dict:
        old = (self.load_profile() or '').strip()
        recent = self._recent_user_dialogue(self.profile_every)
        if not recent.strip():
            return {'profile': old, 'msg': '没有可用的近期对话，画像保持不变'}

        summary = self._summarize_recent(recent, self.profile_every)
        text = (
            f'上一个画像：\n{old or "（暂无）"}\n\n'
            f'最近{self.profile_every}轮对话总结：\n{summary or "（暂无）"}'
        )

        rs = self._get_profile_agent().agent.invoke(
            {'messages': [HumanMessage(content=text)]}
        )
        new_profile = (rs['messages'][-1].content or '').strip()
        if not new_profile:
            return {'summary': summary, 'profile': old, 'msg': '画像模型返回空，保持不变'}

        self.profile.save(new_profile)
        return {'summary': summary, 'profile': new_profile}

    def get_memory_content(self, question: str, recent_rounds: int = 3,
                           top_k: int = 2, max_chars: int = 3000) -> str:
        return self.get_context(
            question=question,
            window_messages=recent_rounds,
            recall_n=top_k,
            exclude_session_id=self.memory_id,
            max_chars=max_chars,
        )

    # 内部小工具
    def _next_turn(self) -> int:
        """轮次 +1（用窗口记忆那个 redis 客户端，不再多建一个连接）"""
        redis_cli = self.windows.redis
        turn = redis_cli.incr(self._turn_key)
        # 和窗口记忆一样的过期时间，会话过期后计数也跟着清
        redis_cli.expire(self._turn_key, self.windows.windows_limit_limit)
        return int(turn)

    def _recent_dialogue(self, rounds: int) -> str:
        """把窗口记忆里最近 rounds 轮（一问一答算一轮）拼成文本"""
        windows = self.load_windows() or []
        recent = windows[-rounds * 2:]
        return '\n'.join(f"{w.get('role')}: {w.get('content')}" for w in recent)

    def _next_profile_turns(self, count: int) -> tuple:
        """用户级画像轮次累加，返回 (增加前, 增加后)

        用单独的 key（不带 memory_id）：画像按用户存，
        换会话后累计轮次不应该从 0 重新数。
        """
        redis_cli = self.windows.redis
        key = self._profile_turn_key

        raw = redis_cli.get(key)
        if isinstance(raw, bytes):
            raw = raw.decode(errors='ignore')

        # 兼容空字符串/脏数据：Redis 对空字符串执行 INCRBY 会报
        # “value is not an integer or out of range”，画像计数会永远卡住。
        try:
            before = int(str(raw).strip()) if raw is not None and str(raw).strip() else 0
        except (TypeError, ValueError):
            before = 0
        if before == 0:
            redis_cli.set(key, 0)

        after = int(redis_cli.incrby(key, count))
        return before, after

    def _recent_user_dialogue(self, rounds: int, max_chars: int = 300,
                              max_total: int = 6000) -> str:
        try:
            messages = self.long.get_recent_history(self.user_id, limit=rounds * 2)
        except Exception as e:
            print(f'[memory] 长期记忆读取失败: {type(e).__name__}: {e}')
            messages = []

        if not messages:
            try:
                windows = self.load_windows() or []
            except Exception:
                windows = []
            messages = [
                f"{w.get('role')}: {w.get('content')}"
                for w in windows[-rounds * 2:]
            ]

        lines = [str(m)[:max_chars] for m in messages if str(m).strip()]
        text = '\n'.join(lines)
        return text[-max_total:] if len(text) > max_total else text

    def _summarize_recent(self, dialogue: str, rounds: int) -> str:
        """把最近 rounds 轮原文压成一段总结（只用于画像更新，不写入会话摘要）"""
        content = (
            f'以下是用户最近 {rounds} 轮对话（跨会话，从旧到新），请总结：\n'
            f'{dialogue}'
        )
        rs = self._get_summary_agent().agent.invoke(
            {'messages': [HumanMessage(content=content)]}
        )
        return (rs['messages'][-1].content or '').strip()

    # 懒加载两个智能体（profile / summary）
    def _get_profile_agent(self):
        if self._profile_agent is None:
            from app.ai.agent.multi_agent.memory.retriever.profile_agent import ProfileAgent
            self._profile_agent = ProfileAgent(self.profile)
        return self._profile_agent

    def _get_summary_agent(self):
        if self._summary_agent is None:
            from app.ai.agent.multi_agent.memory.retriever.summary_agent import SummaryAgent
            self._summary_agent = SummaryAgent(self.summary)
        return self._summary_agent
