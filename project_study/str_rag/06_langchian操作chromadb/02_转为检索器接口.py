from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 加载向量化模型 --- 一定要和创建向量数据库时使用的模型一致
embedding_model = HuggingFaceEmbeddings(
    model_name=r"E:\models\paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={
        "device": "cuda",
        "local_files_only": True,
    },
)
# 加载向量数据库对象
vector_db = Chroma(
    persist_directory=r"./test_db",
    embedding_function=embedding_model,
)
# 转为检索器接口
retriever = vector_db.as_retriever(search_kwargs={"k": 2})
print(retriever)