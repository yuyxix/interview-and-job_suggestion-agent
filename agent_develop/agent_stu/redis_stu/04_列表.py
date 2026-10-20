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

"""
    redis的列表就是一种队列，即消息队列，有着先进先出，后进后出的特点
"""


def test01():
    # 左边添加
    # 设置左右定义从哪边进哪边出
    left_data = client.lpush('user:3', 'a', 'b', 'c')
    # 查询所有元素
    data = client.lrange("user:3", 0, -1)
    print(data)
    print('保存成功')


def test02():
    # 弹出元素，即出队
    # 同理，自定义从左边还是右边弹出元素
    data = client.rpop('user:3')
    print(data)


def test03():
    # 截取, 可用来实现窗口记忆
    client.lpush('user:3', 'a', 'b', 'c')
    # 只保留索引 -2 到 -1 的元素，其余全部删除
    rs = client.ltrim("user:3", -2, -1)
    # 返回布尔值
    print(rs)
    if rs:
        # 获取所有元素
        data = client.lrange("user:3", 0, -1)
        print(data)


if __name__ == '__main__':
    test03()
