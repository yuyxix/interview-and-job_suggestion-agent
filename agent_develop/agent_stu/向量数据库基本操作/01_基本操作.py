import os
import uuid
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

path = os.getenv("CHROMA_PATH")

# 链接数据库
client = chromadb.PersistentClient(path)
print('连接成功')

# 定义向量化模型
embed_fn = SentenceTransformerEmbeddingFunction(
    model_name=r"E:\models\paraphrase-multilingual-MiniLM-L12-v2"
)


# 创建集合
def create_collection():
    # 创建并获取集合
    collection = client.get_or_create_collection(
                    name='test01',
                    embedding_function=embed_fn
    )
    print('集合创建成功')
    return collection


# 保存数据
def save(query, user_id):
    collection = client.get_or_create_collection('test01')
    # id保持唯一性,uuid：用来生成唯一元素的工具类
    ids = f'memory_{user_id} + {uuid.uuid4()}'
    # 添加数据
    collection.add(
        ids=[ids],
        documents=[query],
        metadatas=[
            {"user_id": user_id}
        ]
    )
    print('添加成功')


# 查询数据
def query(user_id, question):
    collection = client.get_or_create_collection('test01')
    # 查询数据库
    rs = collection.query(
        query_texts=[question],
        n_results=3,
        where={"user_id": user_id}
    )
    print('查询成功')
    print(rs['distances'][0])
    print(rs['documents'][0])
    # 查看集合大小
    print(collection.count())


# 删除
def delete(user_id):
    collection = client.get_or_create_collection('test01')
    collection.delete(where={'user_id': user_id})
    print('删除成功')
    print(collection.count())


if __name__ == '__main__':
    # create_collection()
    save('我喜欢看电影', 1)
    save('我喜欢看打游戏', 1)
    save('我喜欢美食', 1)
    save('我正在学习', 1)
    save('我叫小明', 1)
    query(1, '我喜欢什么')
    # delete(1)