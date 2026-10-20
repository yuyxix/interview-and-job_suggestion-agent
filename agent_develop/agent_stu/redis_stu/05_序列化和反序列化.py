import redis
import os
import json
from dotenv import load_dotenv
load_dotenv()

client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    db=int(os.getenv('REDIS_DB'))
)


def test01():
    data = {'name': '张三', 'age': 123}
    # 序列化，把字典类型转换为json字符串
    # ensure_ascii=True会直接把中文转为\u开头的unicode转义符
    # 设为False即可保留原始字符串，直接输出人类可读的形式
    data = json.dumps(data, ensure_ascii=False)
    client.set('user: 1', data)
    print('保存成功')


# 反序列化
def test02():
    data = client.get('user: 1')
    # 反序列化，即把json字符串转换成python对象
    data = json.loads(data)
    print(data)


if __name__ == '__main__':
    test01()