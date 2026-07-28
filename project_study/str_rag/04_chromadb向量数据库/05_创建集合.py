"""
    创建集合，create_collection重要参数：
    1. 集合名称
    2. 向量化模型
"""

import chromadb
from chromadb.utils import embedding_functions


# 获取连接对象
vector = chromadb.PersistentClient('./chroma')
# 设置创建的集合名称
collections_name = 'test01'
# 设置向量化模型 ---目前只能选择这种方式不考虑其他加载方式
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    # 模型名称
    model_name='thenlper/gte-small-zh',
    # 运行设备
    device='cuda',
    # 设置缓存路径
    cache_folder=r'E:\models\gte_small_zh'
)

result = vector.create_collection(
    name=collections_name,  # 集合名称
    embedding_function=embedding_model,  # 自定义嵌入函数
    # 设置向两极之间的比对关系为余弦相似度 --- 默认为l2，欧氏距离
    metadata={'hnsw:space': 'cosine'}
)

print(result)
print(type(result))