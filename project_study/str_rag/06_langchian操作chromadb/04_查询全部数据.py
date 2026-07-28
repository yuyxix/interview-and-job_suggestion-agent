from langchain_chroma import Chroma

vector = Chroma(
    collection_name='hqyj',
    persist_directory='./test_db'
)

# 获取全部数据
result = vector.get()
print(result)