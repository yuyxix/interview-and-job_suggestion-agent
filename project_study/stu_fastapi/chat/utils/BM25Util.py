from rank_bm25 import BM25Okapi
import jieba
from ai import LoadChroma

STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到",
    "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦", "还", "被", "把", "让", "从", "对",
    "与", "但", "而", "或", "所", "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后", "之", "其", "中", "等", "等等", "即",
    "使", "向", "将", "按", "当", "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外", "过",
    "着", "来", "去", "做", "作", "像", "如", "如同", "由于"
}

def BM25_retriever(vector, question):
    # 取出向量数据库中的文档
    documents = vector.get()['documents']
    ids = vector.get()['ids']
    bm25_list = {i: doc for i, doc in zip(ids, documents)}
    # 定义一个分词的函数
    def tokenizer(text):
        result = jieba.cut(text)
        return [token for token in result]
    # 对文档进行分词
    tokens = [tokenizer(doc) for doc in documents]
    # 创建bm25对象
    bm25 = BM25Okapi(tokens)
    question_tokens = tokenizer(question)
    # 计算得分
    bm25_scores = bm25.get_scores(question_tokens)


    # 获取BM25排名结果
    scores_index = [index for index in range(len(bm25_scores))]
    scores_index.sort(key=lambda i: bm25_scores[i], reverse=True)
    bm25_result = {}
    # bm25_result = [documents[index] for index in scores_index[:10]]
    for item in [ids[index] for index in scores_index[:10]]:
        bm25_result.update({item: bm25_list[item]})
    return bm25_result

if __name__ == '__main__':
    vector = LoadChroma.load_chroma_con()
    BM25_retriever(vector, '家庭暴力')