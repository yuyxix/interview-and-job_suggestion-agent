"""
    集合：用于存储数据的容器，数据本质上就是保存在集合中
    不同的项目的数据存储在不同的集合中
    我们操作的内容就是集合
"""

import chromadb

# 获取连接对象
vector = chromadb.PersistentClient(path='./chroma')
# 查看数据库中的所有集合
lists = vector.list_collections()
print(f'所有集合：{lists}')
# 判断某个集合是否存在
try:
    exist = vector.get_collection(name='test01')
    print('集合存在')
except:
    print('集合不存在')
