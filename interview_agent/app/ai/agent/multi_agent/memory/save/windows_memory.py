import redis
import json
import os
from dotenv import load_dotenv
load_dotenv()


# 窗口记忆
class WindowsMemory:
    def __init__(self, session_id, user_id):
        self.redis = redis.StrictRedis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB'))
        )
        self.windows_size = int(os.getenv('WINDOWS_MEMORY_ROUNDS'))
        self.session_id = session_id
        self.user_id = user_id
        # 键里同时带 user_id 和 session_id —— 只按 session_id 的话，
        # 万一传进来一个别人的（或错的）session_id，就会写到别人的会话上
        self.key = f"windows_memory:{self.user_id}:{self.session_id}"
        self.windows_limit_limit = int(os.getenv('WINDOWS_MEMORY_TIME'))

    # 保存记忆
    def save(self, role: str, content: str):
        # 构建字典
        data = {
            "role": role,
            "content": content
        }
        # 添加到队列
        self.redis.rpush(self.key, json.dumps(data, ensure_ascii=False))
        # 保留固定次数的窗口记忆
        self.redis.ltrim(self.key, -self.windows_size, - 1)
        # 设置过期时间
        self.redis.expire(self.key, self.windows_limit_limit)

    # 读取记忆
    def query(self):
        # 判断键是否存在
        if self.redis.exists(self.key):
            # 反序列化
            data = self.redis.lrange(self.key, 0, -1)
            return [json.loads(item) for item in data]
        return None
