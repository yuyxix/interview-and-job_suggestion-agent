import chromadb
import os

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
import uuid

load_dotenv()

"""
    长期记忆存储
"""


class LongMemory:
    def __init__(self):
        load_dotenv()
        path = os.getenv("CHROMA_PATH")
        # 链接数据库
        client = chromadb.PersistentClient(path)
        # 向量化模型
        embed_fn = SentenceTransformerEmbeddingFunction(
            model_name=r"E:\models\paraphrase-multilingual-MiniLM-L12-v2"
        )
        # 创建集合
        self.collection = client.get_or_create_collection(
            name='long_memory',
            embedding_function=embed_fn
        )

        # 添加内容
        # 保存数据
    def save(self, user_id, query):
        # id保持唯一性,uuid：用来生成唯一元素的工具类
        ids = f'memory_{user_id} + {uuid.uuid4()}'
        # 添加数据
        self.collection.add(
            ids=[ids],
            documents=[query],
            metadatas=[
                {"user_id": user_id}
            ]
        )

    # 查询数据
    def query(self, user_id, question):
        # 查询数据库
        rs = self.collection.query(
            query_texts=[question],
            n_results=3,
            where={"user_id": user_id}
        )
        return rs['documents'][0]


if __name__ == '__main__':
    memory = LongMemory()
    rs = memory.query(1, '我爱游戏')
    print(rs)

