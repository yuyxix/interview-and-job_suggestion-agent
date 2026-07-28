import chromadb

# 获取连接对象
vector = chromadb.PersistentClient('./chroma')
# 设置创建对象名称
collections_name = 'test01'
# 获取集合对象
collection = vector.get_collection(name=collections_name)
# 准备测试数据 --- 后期这个数据的来源为自己的RAG系统的知识库的数据来源，，如txt, pdf ....
docs = [
    "小明喜欢苹果",
    "小红喜欢香蕉",
    "小刚喜欢橙子"
]
#  调用add方法
result = collection.add(
    documents=docs,
    ids=[f'doc{str(i)}' for i in range(len(docs))],
    metadatas=[{"category": "like_fruit"} for _ in range(len(docs))],
    )
print('添加文档成功')