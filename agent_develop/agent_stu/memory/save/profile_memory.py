import redis
import os
from dotenv import load_dotenv
load_dotenv()

"""
    用户画像记忆存储
"""


class ProfileMemory:
    def __init__(self, user_id):
        self.redis = redis.StrictRedis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB'))
        )
        self.key = f'profile: {user_id}'

    # 保存
    def save(self, hashkey, value):
        self.redis.hset(self.key, hashkey, value)

    # 查询
    def query(self):
        # 查询特定用户的画像
        rs = self.redis.hgetall(self.key)
        data = ''
        if rs:
            for hashkey, value in rs.items():
                data += f'{hashkey.decode()}:{self.redis.hget(self.key, hashkey).decode()}\n'
        print(data)


if __name__ == '__main__':
    p = ProfileMemory(1)
    p.save('name', '张三')
    p.save('age', 23)
    p.query()