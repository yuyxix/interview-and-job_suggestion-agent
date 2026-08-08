'''
    存在问题，如果两个算法检索结果不同的话，不同的那部分内容没法纳入计算
'''

# 假设向量检索结果
one = [{"D1": 0.35}, {"D2": 0.25}, {"D3": 0.15}, {"D4": 0.05}]
# 假设BM25结果
two = [{"D2": 35}, {"D4": 25}, {"D3": 15}, {"D1": 5}]

# 使用RRF算法融合两个检索结果，然后筛选top-2
results = []
# 遍历向量检索结果
for i, vector_item in enumerate(one, start=1):
    # 遍历向量检索结果的所有key
    for vector_key in vector_item.keys():
        # 遍历BM25检索结果
        for j, bm25_item in enumerate(two, start=1):
            # 遍历BM25检索结果所有key
            for bm25_key in bm25_item.keys():
                # 如果向量检索结果和BM25结果key相同
                if vector_key == bm25_key:
                    # rrf融合
                    results.append({
                        vector_key: (1/(60+i) + 1/(60+j))
                    })
print(results)
# 排序
# 截取

