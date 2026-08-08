# 构造RAG向量数据库数据集
from langchain_chroma import Chroma
from langchain_core.documents import Document

from ai import LoadEmbeddingModel
import pandas as pd

# 数据集路径
database_path = r'E:\workspace\project_study\stu_fastapi\create_data\法律数据集.csv'
# 向量数据库存储路径
vector_database_path = r'E:\workspace\project_study\stu_fastapi\law_chroma'
# 集合名称
collection_name = 'law'

# pandas 读取数据
df = pd.read_csv(database_path)
# <DataFrame>转list
data_List = df['text'].tolist()
# 转list[Document]
documents = [Document(page_content=text, metadata={'source': database_path}) for text in data_List]

# 存入向量数据库
try:
    Chroma.from_documents(
        documents=documents,
        embedding=LoadEmbeddingModel.load_embedding_model(),
        persist_directory=vector_database_path,
        collection_name=collection_name,
        collection_metadata={'hnsw:space': 'cosine'}
    )
    print('数据存入成功')
except Exception as e:
    print(f'数据存入失败:{e}')