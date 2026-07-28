import chromadb

# 获取连接对象
vector = chromadb.PersistentClient('./chroma')
# 设置创建对象名称
collections_name = 'test01'
# 获取集合对象
collection = vector.get_collection(name=collections_name)

"""
get方法：获取文档内容，可以参看get的api来使用 --- 无返回值
"""
# 不设参数直接获取文档内容，默认包含"metadatas", "documents"
'''
 等价于
 result = collection.get(
    include=["metadatas", "documents"],  # 检索包含的内容
)
'''
result = collection.get()
print(result)

print('=' * 50)

# 指定检索的ids
result = collection.get(
    ids=["doc0"],  # 检索的文档
    include=["metadatas", "documents"],  # 检索包含的内容
)

print(result)
print('=' * 50)
# 分别用where和where document参数来检索，注意其区别

# where：元数据过滤
# 更多检索的比较操作符见get的api
result = collection.get(
    include=["metadatas", "documents"],  # 检索包含的内容
    where={'category': 'like_fruit'}      # 只返回类别=水果的文档
)
print(result)
print('=' * 50)

# where_document
result = collection.get(
    include=["metadatas", "documents"],  # 检索包含的内容
    where_document={"$contains": "苹果"} # 查询document中包含"苹果"的文档
)
print(result)
