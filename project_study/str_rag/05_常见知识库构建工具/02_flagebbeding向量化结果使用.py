import numpy as np
from FlagEmbedding import FlagAutoModel



# 加载向量化模型
embedding_model = FlagAutoModel.from_finetuned(
    # 模型路径 --- 名称BAAI/bge-base-zh-v1.5
    model_name_or_path=r'E:\models\bge-base-zh-v1.5',
    # 模型缓存目录
    cache_dir=r'E:\models\bge-base-zh-v1.5',
    # 检索指令
    query_instruction_for_retrieval='为这个句子生成表示以用于检索相关文章：',
    # 半精度
    use_fp16=True
)
# 加载npz文件 --- 数据
data = np.load(r'E:\workspace\project_study\str_rag\datasets\flag_embedding.npz')
# 获取原始文档
docs = data['documents']
print(data)
print(docs)
print(data['embedding_docs'])
# 获取向量化数据
embeddings = data['embedding_docs']

# 测试问题
question = "RAG是什么？"
# 问题向量化
question_embedding = embedding_model.encode(question)

# 定义一个余弦相似度函数
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 定义一个存放所有结果得分的列表
score_list = [{index: cosine_similarity(item, question_embedding)} for index, item in enumerate(embeddings)]
print(f"得分列表：\n{score_list}")
# 排序 --- x 表示score_list中的每一个元素，list(x.values())[0]表示获取字典中的第一个值按照这个排序
score_list.sort(key=lambda x: list(x.values())[0], reverse=True)
print(f"排序后得分列表：\n{score_list}")
# 获取top_k的文档
top_k = 3

for index, item in enumerate(score_list[:top_k]):
    for one in item.keys():
        print(f'top-{index+1}文档：\n{docs[one]}')

