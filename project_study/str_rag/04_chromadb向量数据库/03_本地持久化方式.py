import chromadb

"""
    PersistentClient: 本地持久化方式
    参数：
        1.path:数据库存储路径

"""
vector = chromadb.PersistentClient(
    path="./chroma",
)

print(vector)