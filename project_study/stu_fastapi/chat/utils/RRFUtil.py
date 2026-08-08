def rrf_util(retriever):
    score_list = []
    for i, vector_item in enumerate(retriever, start=1):
        score_one = (1 / (60 + i))
        score_list.append(score_one)
    rrf_result = {key: score for key, score in dict(zip(list(retriever.keys()), score_list)).items()}
    return rrf_result

# def rrf_retriever(rrf_one, rrf_two):
#     # rrf算法融合
#     retriever_result = {}
#     for i in rrf_one.keys:
#         if i not in rrf_two:
#             retriever_result.update(i)
#     for j in rrf_two.keys():
#         if j not in rrf_one:
#             retriever_result.update(j)
#     for i in rrf_one.keys():
#         for j in rrf_two.keys():
#             if i == j:
#                 retriever_result.update()
#     print(retriever_result)



if __name__ == '__main__':
    rrf_util({'a': 1, 'b': 2})