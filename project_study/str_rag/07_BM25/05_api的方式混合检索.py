from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

# 准备测试数据
documents = [
    "苹果公司发布了新款iPhone 15 Pro Max，搭载A17 Pro芯片",
    "苹果是一种营养丰富的水果，含有丰富的维生素C",
    "苹果公司的CEO蒂姆·库克在WWDC上发布了Apple Intelligence",
    "每天吃一个苹果有益健康，医生远离我",
]

# 把数据包装为list[Document]格式
docs = [Document(page_content=doc, metadata={'id': f'{index}'}) for index, doc in enumerate(documents, start=1)]

# 加载向量化模型
embedding_model = HuggingFaceEmbeddings(
    model_name=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
    model_kwargs={
        'device': 'cuda',
        'local_files_only': True,

    }
)

# 把数据存入向量数据库中
vector_db = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory=r'E:\workspace\project_study\str_rag\chroma',
    collection_name='demo',
)

# 创建向量检索器
vector_retrievers = vector_db.as_retriever(search_kwargs={'k': 3})

# 创建BM25检索器 --- 返回3条数据
bm25_retrievers = BM25Retriever.from_documents(
    documents=docs,
    k=3
)

# 创建ensemble检索其 --- 混合检索器
ensemble_retrievers = EnsembleRetriever(
    retrievers=[vector_retrievers, bm25_retrievers]
)

question = '苹果公司最新动态是什么？'

results = ensemble_retrievers.invoke(question)
print(results)