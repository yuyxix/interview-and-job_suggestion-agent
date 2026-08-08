'''
    安装BM25和分词用的 jieba 的库
    pip install rank_bm25 jieba
'''
from rank_bm25 import BM25Okapi


# 准备文档集
documents = [
    # 科技类 —— 苹果公司
    "苹果公司市值突破三万亿，成为全球最有价值的科技公司",
    "苹果公司将在新款MacBook上采用自研M3芯片，性能大幅提升",
    # 科技类 —— 其他公司
    "华为Mate60搭载麒麟芯片强势回归，引发市场广泛关注",
    # 水果类
    "苹果是一种营养丰富的水果，含有丰富的维生素和膳食纤维",
    "每天吃一个苹果有益健康，可以降低胆固醇并帮助消化",
    "红富士苹果产地直供，新鲜采摘，脆甜多汁口感极佳",
    "水果市场行情分析：苹果价格稳定，柑橘类水果销量上升",
]

# 作假分词
tokens = [item.split(' ') for item in documents]
print(tokens)

# 创建BM25对象
bm25 = BM25Okapi(tokens)

# 问题以及对问题进行分词
question = "苹果公司市值"
question_tokens = question.split(' ')

# 用get_scores方法获取得分
scores = bm25.get_scores(question_tokens)
# 因为是假分词，没有真正转化为token，所以没法得出真正的分数
print(scores)