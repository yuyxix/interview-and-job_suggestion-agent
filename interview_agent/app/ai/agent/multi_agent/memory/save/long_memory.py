from dotenv import load_dotenv
import time
import uuid
from fastapi.requests import Request
load_dotenv()


# 长期记忆，通过向量数据库存储，同时也方便检索
class LongMemory:
    def __init__(self, request: Request):
        self.collection = request.app.state.collection

    @staticmethod
    def _where(user_id, session_id=None):
        """拼 Chroma 的 where 条件（统一入口，别在各处手写）

        ⚠️ Chroma 1.x 的硬要求：where 顶层【只能有一个操作符】。
           两个条件直接平铺 —— {'user_id': 'u1', 'session_id': 's1'} —— 会报：
               ValueError: Expected where to have exactly one operator, got {...}
           必须包进 $and：{'$and': [{'user_id': 'u1'}, {'session_id': 's1'}]}
           （实测：单个条件平铺是 OK 的，只有多条件才需要 $and）
        """
        # ★ 统一转成字符串，和 save() 里存进去的类型对上 ——
        #   Chroma 的 $eq 是【类型敏感】的：存的是 int 1，拿字符串 '1' 查就是查不到。
        #   这个坑特别难查：数据在、条件也对，就是没结果。
        conds = [{'user_id': {'$eq': str(user_id)}}]
        if session_id:
            conds.append({'session_id': {'$eq': str(session_id)}})
        return conds[0] if len(conds) == 1 else {'$and': conds}

    def save(self, session_id, user_id, messages):
        ids = f'memory_{session_id} + {uuid.uuid4()}'
        # 添加数据
        self.collection.add(
            ids=[ids],
            documents=[messages],
            # session_id 必须一起存进去：get_history() 是按 session_id 过滤的，
            # 不存这里，按会话取对话永远查不到东西
            #
            # ★ user_id / session_id 一律转成字符串 —— 见 _where() 里的说明，
            #   Chroma 的 $eq 类型敏感，存 int 查字符串就是查不到
            metadatas=[{
                "user_id": str(user_id),
                "session_id": str(session_id),
                # 画像每 20 轮要取"最近的对话"，而 Chroma 的 get 不保证顺序，
                # 只能自己记时间、取回后排序
                "save_time": time.time(),
            }]
        )

    # 查询数据
    def query(self, user_id, question, session_id=None, exclude_session_id=None,
              n_results=3):
        """按问题召回

        · user_id 必须传 —— 保证不会召回别人的记忆
        · session_id 传了 → 只在这段会话里召回
        · exclude_session_id 传了 → 排除这段会话（拼上下文时排除"当前会话"，
          否则会和窗口记忆里的最近几轮重复，同一句话出现两次）
        · 都不传 → 跨会话召回（长期记忆的默认行为）
        """
        conds = [{'user_id': {'$eq': str(user_id)}}]
        if session_id:
            conds.append({'session_id': {'$eq': str(session_id)}})
        if exclude_session_id:
            # $ne：排除当前会话（实测 Chroma 支持）
            conds.append({'session_id': {'$ne': str(exclude_session_id)}})
        where = conds[0] if len(conds) == 1 else {'$and': conds}

        rs = self.collection.query(
            query_texts=[question],
            n_results=n_results,
            where=where
        )
        return rs['documents'][0]

    # 记忆检索：在这段会话里按关键词找，返回命中记录 + 它在会话里的位置
    def search_memory(self, user_id, session_id, keyword):
        """返回 [{'index','role','content','document_id'}, ...]；没命中就是空列表

        为什么要重新 get 一遍，而不是复用 get_history()：
          get_history() 最后 return 的是 rs['documents'] —— 只有文本，
          ids 和顺序全丢了；而"定位到第几条"和"删掉某一条"恰恰需要这两个。
        """
        rs = self.collection.get(
            where=self._where(user_id, session_id),
            # include 里不能有 'ids'（永远会返回），只有 documents / metadatas 之类
            include=['documents', 'metadatas'],
        )
        documents = rs.get('documents') or []
        ids = rs.get('ids') or []

        matches = []
        # 注意：documents 是【字符串列表】，不是字典列表 ——
        # 之前写的 memory_message.keys() 会直接 AttributeError
        for index, doc in enumerate(documents):
            if keyword and keyword in doc:
                role, _, _ = doc.partition(':')      # 存的时候是 'user: xxx' / 'ai: xxx'
                matches.append({
                    'index': index,                  # 在这段会话里排第几（从 0 开始）—— 前端滚动定位用
                    'role': role.strip(),
                    'content': doc,
                    'document_id': ids[index],       # 删单条时用它
                })
        return matches

    # 获取该用户最近的对话（跨会话，按时间升序）
    def get_recent_history(self, user_id, limit=None):
        """取该用户所有会话的对话原文，按 save_time 升序返回最后 limit 条

        画像更新要"最近 20 轮"（一问一答算一轮 → 40 条消息），
        而 Chroma 的 get 不保证顺序，所以在 metadata 里存了 save_time。
        老数据没有 save_time 的按 0 处理，用返回顺序兜底。
        """
        rs = self.collection.get(
            where={'user_id': {'$eq': str(user_id)}},
            include=['documents', 'metadatas'],
        )
        documents = rs.get('documents') or []
        metadatas = rs.get('metadatas') or []

        rows = []
        for index, (doc, meta) in enumerate(zip(documents, metadatas)):
            save_time = (meta or {}).get('save_time') or 0
            rows.append((save_time, index, doc))
        rows.sort(key=lambda row: (row[0], row[1]))

        documents = [doc for _, _, doc in rows]
        return documents[-limit:] if limit else documents

    #  获取对话内容
    def get_history(self, user_id, session_id):
        rs = self.collection.get(
            where=self._where(user_id, session_id),
            # ⚠️ include 里不能写 'ids'（它永远会返回），也不能写 'metadata'（是 metadatas 复数）——
            #    原来写的是 ['documents','ids','metadata']，两个都错，Chroma 1.x 会直接报
            #    "Expected include item to be one of documents, embeddings, metadatas..."
            include=['documents', 'metadatas']
        )
        return rs['documents']

    # 删除整段会话的对话记录
    def delete(self, user_id, session_id):
        """按 (user_id, session_id) 删掉这段会话的全部对话"""
        # ★ where 的写法：Chroma 只认【字段名 -> 值/操作符】，metadata 里的字段是【平铺】进来的。
        #   原来写的 where={'metadata': [...]} 里那个 'metadata' 键根本不存在，
        #   要么报错、要么永远查不到 → result['ids'] 一直是空 → 永远走"记录不存在"分支
        result = self.collection.get(
            where=self._where(user_id, session_id)
        )
        ids = result.get('ids') or []
        if not ids:
            print('记录不存在')
            return {
                'code': 500,
                'msg': '这段会话没有对话记录',
                'data': {'deleted': 0}
            }
        self.collection.delete(ids=ids)
        print(f'删除对话记录成功：{len(ids)} 条')
        return {
            'code': 200,
            'msg': f'已删除 {len(ids)} 条对话记录',
            'data': {'deleted': len(ids)}
        }
