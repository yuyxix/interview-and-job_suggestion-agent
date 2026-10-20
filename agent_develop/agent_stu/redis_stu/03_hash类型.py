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


def test01():
    client.hset('user:1', 'name', '李四')
    client.hset('user:1', 'email', '111@qq.com')
    client.hset('user:1', 'department', '部门')
    client.hset('user:2', 'name', '张三')
    # 设置失效时间
    client.expire('user:2', 15)
    print('保存成功')


def test02():
    rs = client.hgetall('user:1')
    if rs:
        name = client.hget('user:1', 'name').decode()
        email = client.hget('user:1', 'email').decode()
        department = client.hget('user:1', 'department').decode()
        print(f'name: {name}, email: {email}, department: {department}')
    else:
        print('数据不存在')
if __name__ == '__main__':
    test02()