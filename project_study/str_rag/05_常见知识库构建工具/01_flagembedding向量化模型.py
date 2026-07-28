import numpy as np
from FlagEmbedding import FlagAutoModel
# 准备测试数据
documents = [
        "FlagEmbedding 是一个由北京智源人工智能研究院开发的文本嵌入模型。",
        "它可以将文本转换为高维向量，用于计算语义相似度。",
        "BGE 模型在 Massive Text Embedding Benchmark (MTEB) 排行榜上取得了优异的成绩。",
        "RAG（检索增强生成）是一种利用外部知识库来增强大模型回答能力的技术。",
        "苹果公司由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗恩·韦恩于 1976 年创立。",
        "苹果最新款的智能手机是 iPhone 15系列，搭载了A17 Pro芯片。",
        "熊猫是中国的国宝，主要栖息地是四川、陕西和甘肃的山区。",
        "深度学习是机器学习的一个分支，它基于深层神经网络。"
    ]

# 加载向量化模型
embedding_model = FlagAutoModel.from_finetuned(
    # 模型路径 --- 名称BAAI/bge-base-zh-v1.5
    model_name_or_path=r'E:\models\bge-base-zh-v1.5',
    # 模型缓存目录
    cache_dir=r'E:\models\bge-base-zh-v1.5',
    # 检索指令
    query_instruction_for_retrieval='为这个句子生成表示以用于检索相关文章：',
    # 半精度
    # use_fp16=True 表示启用 FP16（半精度浮点数） 来加载和运行模型。
    # FP16：每个数值用 16 位存储（相比 FP32 的 32 位），显存占用减半，计算速度更快
    # 代价：精度略有损失，但对文本向量化任务的最终效果影响极小
    # 前提：需要 GPU 支持（如你的 device: cuda 环境），CPU 上通常不支持 FP16 加速
    use_fp16=True
)
# 向量化数据
embedding_docs = embedding_model.encode(documents)
# 存储向量化数据
'''
    参数：
        1. 存储的文件名
        2. 存储的原始文本数据
        3. 存储的向量化数据
'''

np.savez(
    r'E:\workspace\project_study\str_rag\datasets\flag_embedding.npz',
    documents=documents,
    embedding_docs=embedding_docs
)