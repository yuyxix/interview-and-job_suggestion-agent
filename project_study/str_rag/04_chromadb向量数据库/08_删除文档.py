import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma")
collection = chroma_client.get_or_create_collection(name="test01")

# 查看当前集合中所有文档
result = collection.get(
    include=["documents", "metadatas", "embeddings"]
)
print(result)

# 根据 id 删除
collection.delete(ids=["doc1"])
# 查看当前集合中所有剩余文档
result = collection.get(
    include=["documents", "metadatas", "embeddings"]
)
print(result)

# 按条件删除（通过元数据过滤）
collection.delete(
    where={"category": "水果爱好"}
)
# 查看当前集合中所有剩余文档
result = collection.get(
    include=["documents", "metadatas", "embeddings"]
)
print(result)