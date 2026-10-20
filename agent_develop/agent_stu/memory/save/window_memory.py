import redis
import json
import os
from dotenv import load_dotenv
load_dotenv()


"""
    短期记忆 --- 窗口记忆
    这里的技术选型就是通过redis的队列，将对话保存起来，
    再用队列截断的特性来实现窗口记忆
"""


class WindowsMemory:

    def __init__(self, session_id):
        self.redis = redis.StrictRedis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB'))
        )
        self.windows_size = int(os.getenv('WINDOWS_MEMORY_ROUNDS'))
        self.session_id = session_id
        self.key = f"windows_memory:{self.session_id}"
        self.windows_limit_time = int(os.getenv('WINDOWS_MEMORY_TIME'))

    # 保存记忆
    def save(self, role: str, content: str):
        # 构建一个字典
        data = {'role': role, 'content': content}
        # 添加到列表，即队列
        self.redis.rpush(self.key, json.dumps(data, ensure_ascii=False))
        # 保留固定次数的窗口记忆
        self.redis.ltrim(self.key, -self.windows_size, -1)
        # 设置过期时间
        self.redis.expire(self.key, self.windows_limit_time)

    # 读取记忆
    def query(self):
        # 判断键是否存在
        if self.redis.exists(self.key):
            # 反序列化
            data = self.redis.lrange(self.key, 0, -1)
            return [json.loads(i) for i in data]
        return []


if __name__ == '__main__':
    memory = WindowsMemory('001')
    # 模拟人类消息添加
    memory.save("user", "你好")
    # 模拟AI回复消息
    memory.save("ai", "你好，我是AI助手")
    # 模拟人类消息添加
    memory.save("user", "你好1")
    # 模拟AI回复消息
    memory.save("ai", "你好1，我是AI助手1")
    # 模拟人类消息添加
    memory.save("user", "你好2")
    # 模拟AI回复消息
    memory.save("ai", "你好2，我是AI助手2")
    memory.save("user", "你好3")
    # 模拟AI回复消息
    memory.save("ai", "你好3，我是AI助手2")
    # 查询记忆
    rs = memory.query('001')
    print(rs)