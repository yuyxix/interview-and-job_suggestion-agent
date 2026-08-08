from transformers import AutoTokenizer, AutoModel
import torch

# 测试数据
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

# 加载分词模型
tokenizer = AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path=r'E:\models\bge-base-zh-v1.5',
)
# 加载模型
model = AutoModel.from_pretrained(
    pretrained_model_name_or_path=r'E:\models\bge-base-zh-v1.5',
)
# 模型评估模式
model.eval()


# 封装得到文本向量的函数
def get_embeddings(texts):
    # 分词模型处理输入的文本#
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    # 计算token向量
    with torch.no_grad():
        model_output = model(**encoded_input)
        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = model_output[0][:, 0]
        # 归一化向量化结果
        return torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)


# 调用get_embeddings处理文档 ---> 向量
docs_embeddings = get_embeddings(documents)
# 准备查询问题
question = "什么是深度学习?"
question_embeddings = get_embeddings([question])
# 获取相似度
similarity = torch.matmul(docs_embeddings, question_embeddings.T)
# 打印结果
print(f"相似度：{similarity}")
# 处理结果 --- 结果为 tensor，我们要转为 list
scores = [{index: round(item[0], 2)} for index, item in enumerate(similarity.tolist())]
print(scores)


