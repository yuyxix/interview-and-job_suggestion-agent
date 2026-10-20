import redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_con():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB')),
        # 注意：不要传 protocol=2 —— 那是 redis-py 5.0 才有的参数，
        # 本项目装的是 4.5.5，传了会直接 TypeError。不传默认就是 RESP2。
        # 设置返回数据为字符串
        decode_responses=True
    )

# 关闭连接
def close_redis_con(con):
    con.close()