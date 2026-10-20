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


def test():
    # 初始化的自增变量
    client.set('count', 0)
    if client.ping():
        client.set('name', '李四')
        client.set('age', 23)
        client.set('sex', '男')
        # ex用来设置存储时间
        client.set('address', '成都', ex=60)
        # 开发中，保存键名唯一性，防止键名相同而被覆盖
        print('数据保存成功')

        # 自增
        client.incr('count')
        # redis取值,取值默认返回byte类型，需要解码
        if client.get('name'):
            name = client.get('name').decode()
            age = client.get('age').decode()
            sex = client.get('sex').decode()
            print(name, age, sex)
        else:
            print('数据不存在')
    else:
        print('redis服务启动失败')


def test01():
    # 自增
    client.incr('count')
    num = client.get('count')
    print(f'num={num}')


def test02():
    # 自减
    client.decr('count')
    num = client.get('count')
    print(f'num={num}')


if __name__ == '__main__':
    test01()