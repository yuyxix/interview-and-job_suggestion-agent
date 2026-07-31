import redis
from dotenv import load_dotenv
import os

load_dotenv()

def get_redis_conn():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB')),
        protocol=2,
        # 设置返回数据为字符串
        decode_responses=True
    )

# 关闭连接
def close_redis_conn(conn):
    conn.close()