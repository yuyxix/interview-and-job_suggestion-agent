from rank_bm25 import BM25Okapi
import jieba

# 准备文档集
# 准备文档集
documents = [
    "苹果公司市值突破三万亿，成为全球最有价值的科技公司",
    "苹果是一种营养丰富的水果，含有丰富的维生素和膳食纤维",
    "每天吃一个苹果有益健康，可以降低胆固醇并帮助消化",
    "三星发布了新一代折叠屏手机Galaxy Z Fold，采用钛合金铰链",
    "水果市场行情分析：苹果价格稳定，柑橘类水果销量上升",
    "苹果公司发布了新款iPhone 15，搭载A17芯片和潜望式长焦镜头",
    "红富士苹果产地直供，新鲜采摘，脆甜多汁口感极佳",
    "苹果公司将在新款MacBook上采用自研M3芯片，性能大幅提升",
    "华为Mate 60搭载麒麟芯片强势回归，引发市场广泛关注",
    "苹果公司CEO蒂姆·库克在秋季发布会上介绍了Vision Pro头显设备",
]

# 中文停用词表（常见停用词，避免无意义词干扰BM25排序）
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦",
    "还", "被", "把", "让", "从", "对", "与", "但", "而", "或", "所",
    "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后",
    "之", "其", "中", "等", "等等", "即", "使", "向", "将", "按", "当",
    "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外",
    "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于",
])

# 定义分词函数
def tokenize(text):
    result = jieba.cut(text)
    return [token for token in result]

# 分词
tokens = [tokenize(doc) for doc in documents]
print(tokens)

# 对问题分词
question = "苹果公司市值"
question_tokens = tokenize(question)

# 创建BM25对象
bm25 = BM25Okapi(tokens)

# 得分
bm25_scores = bm25.get_scores(question_tokens)
print(bm25_scores)

# 获取BM25索引排序结果
scores_index = [index for index in range(len(bm25_scores))]
scores_index.sort(key=lambda x: bm25_scores[x], reverse=True)

print(f'原始结果：{scores_index}')

# 获取BM25排序结果
results = [documents[index] for index in scores_index[:3]]
print(f'排序后的结果:{results}')

