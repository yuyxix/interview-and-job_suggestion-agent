import redis
import os
from dotenv import load_dotenv
from redis.exceptions import ResponseError
load_dotenv()

"""
    用户画像记忆存储

    一个用户只存一份完整画像（一个 Redis 字符串 key），每次更新整份覆盖，
    不再拆成 name / age / job ... 多个 Hash 字段。
"""


class ProfileMemory:
    def __init__(self, user_id):
        self.redis = redis.StrictRedis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB'))
        )
        # 去掉键里多余的空格（原来拼出来是 'profile: 123'，排查时容易看错）
        self.key = f'profile:{user_id}'

    # 保存：整份画像覆盖写入
    def save(self, profile: str):
        try:
            self.redis.set(self.key, profile)
        except ResponseError:
            # 旧版本把画像存成 Hash 的多个字段，类型不同不能直接 SET。
            # 旧字段内容已经由 query() 读出来参与合并了，这里清掉旧结构，
            # 换成"一个用户一个字段"的字符串存储。
            self.redis.delete(self.key)
            self.redis.set(self.key, profile)

    # 查询：返回整份画像文本
    def query(self):
        try:
            value = self.redis.get(self.key)
            # 必须 return：调用方（记忆管理器）要拿这个结果拼 prompt
            return value.decode() if value else ''
        except ResponseError:
            # 兼容旧版 Hash 结构：拼成多行文本参与这轮合并，
            # 下一次 save() 会自动迁移成单字段字符串
            old = self.redis.hgetall(self.key)
            if not old:
                return ''
            return '\n'.join(
                f'{k.decode()}: {v.decode()}' for k, v in old.items()
            )