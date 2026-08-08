# 假设向量检索结果
one = [{"D1": 0.35}, {"D2": 0.25}, {"D3": 0.15}, {"D4": 0.05}]
# 假设BM25结果
two = [{"D2": 35}, {"D5": 25}, {"D3": 15}, {"D1": 5}]

# 使用RRF算法融合两个检索结果，然后筛选top-2
# 遍历向量检索结果
result_one = []
for i, vector_item in enumerate(one, start=1):
    print(i, vector_item)
    score_one = (1/(60+i))
    # 遍历向量检索结果的所有key
    for vector_key in vector_item.keys():
        result_one.append({vector_key: score_one})
        print(vector_key)
print(result_one)
# 遍历BM25检索结果
result_two = []
for j, bm25_item in enumerate(two, start=1):
    score_two = (1 / (60 + j))
    # 遍历BM25检索结果所有key
    for bm25_key in bm25_item.keys():
        result_two.append({bm25_key: score_two})
print(result_two)

result = {}

for i in result_one:
    if i.keys() not in result_two:
        result.update(i)
for j in result_two:
    if j.keys() not in result_one:
        result.update(j)
for i in result_two:
    for j in result_one:
        if i.keys() == j.keys():
            for key_one in i.keys():
                for key_two in j.keys():
                    result.update({key_one: i[key_one] + j[key_two]})

print(result)


