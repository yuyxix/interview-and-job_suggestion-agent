import numpy as np
from FlagEmbedding import FlagAutoModel
from FlagEmbedding import FlagReranker


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
retriever_result = []
for index, item in enumerate(score_list[:top_k]):
    for one in item.keys():
        print(f'top-{index+1}文档：\n{docs[one]}')
        retriever_result.append(docs[one])
print(f'retriever_result: \n{retriever_result}')
print('---------------------------对召回结果进行重排序---------------------------')
'''
    把question和召回【粗排】的文档再次计算 --- 通过重排序模型来实现【重排序模型一般都是cross-encoder】
    --- 本质上就是计算question和召回的文档之间的相似度【自注意力机制来实现的】 --- 精排
    过程：
        需要把问题和召回的文档包装成(question, doc1),(question, doc2)...
    重排序发生在粗排之后，注入上下文给大模型之前

'''

# 加载重排序模型
reranker = FlagReranker(
    model_name_or_path=r'E:\models\bge-reranker-large_v1',
    use_fp16=True
)
# 把问题和召回的文档包装
reranker_input = [
    (question, doc) for doc in retriever_result
]
print(reranker_input)
scores = reranker.compute_score(reranker_input)
print(scores)