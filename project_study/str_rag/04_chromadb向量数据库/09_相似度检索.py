'''

query方法就是用来完成问题和数据库中的文档之间相似度匹配，然后返回top_k的方法

'''

import chromadb

# 获取连接对象
vector = chromadb.PersistentClient('./chroma')
# 设置创建的集合名称
collections_name = 'test01'
# 获取集合对象
collection = vector.get_collection(name=collections_name)
