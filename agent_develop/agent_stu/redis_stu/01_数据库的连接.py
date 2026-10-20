import redis
import os
from dotenv import load_dotenv
load_dotenv()

client = redis.StrictRedis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        db=int(os.getenv('REDIS_DB'))
    )

if client.ping():
    print('redis服务启动成功')

else:
    print('redis服务启动失败')