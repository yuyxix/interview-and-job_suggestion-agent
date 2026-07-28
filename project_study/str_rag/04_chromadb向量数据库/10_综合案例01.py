# 使用langchain封装的回答链RAG retrieverQA数据链

'''
    注意：langchain封装封装的API和chroma库中的API不一样，不要混淆，一个是langchain_chroma，一个是chroma
    一.langchain封装chromadb的API实现流程：
        1.构造向量数据库数据内容
        2.数据分块
        3.加载向量化模型
        4.创建向量数据库然后存入数据【创建向量数据库的时候直接指定存储路径和集合名称】
    二.问答 ---外部知识数据库的查询结果作为上下文，然后模型生成回复
        1.加载向量数据库
        2.加载模型，向量化模型
        3.得到向量数据库对象创建问答链
        4.生成回复【本质上是通过问答链来完成的，不是直接用大模型生成回复，大模型这个时候已经放在langchain的链
        里面去了，它会自动地去检索当前问题相关的文档，然后基于相关文档【模型回复上下文】来回答当前的问题】
'''

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
import os
from langchain_classic.chains.retrieval_qa.base import RetrievalQA

# 数据分块 --- 存储位置 --- 集合名称 --- 模型名称
database_path = r"E:\workspace\project_study\str_rag\datasets\华清远见.txt"
# 存储位置
vector_path = r"E:\workspace\project_study\str_rag\04_chromadb向量数据库\lc_chroma"
# 集合名称
collection_name = "hqyj"
# 模型名称
embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# embedding模型存储路径
embedding_model_path = r"E:\models\paraphrase-multilingual-MiniLM-L12-v2"
# 加载模型对象
chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-max-preview",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
    streaming=False
)


# 创建向量数据库并存入数据
def build_vector_db():
    loader = TextLoader(
        file_path=database_path,  # 加载的文件路径
        encoding='utf-8',  # 设置编码
    )
    document = loader.load()

    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", ".", "？", "！", "\n"]
    )
    # 执行分块
    chunks = text_splitter.split_documents(document)
    print(chunks)
    # 加载向量化模型
    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        cache_folder=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
        # 执行本地模型
        model_kwargs={
            'device': 'cuda',
            'local_files_only': True
        }
    )

    # 创建向量数据库并存入数据 --- 一步到位，直接就把数据存入到了向量数据库中
    vector_db = Chroma.from_documents(
        # 数据内容
        documents=chunks,
        # 选向量化模型
        embedding=embedding_model,
        # 集合名称
        collection_name=collection_name,
        # 存储位置
        persist_directory=vector_path
    )
# 加载数据库对象
# 查看集合是否创建成功，文档是否成功添加
def query_vector_db():
    vector_db = Chroma(persist_directory=vector_path, collection_name=collection_name)
    print(vector_db.get())

# 问答一：不使用RAG
def qa_no_rag():
    messages = [
        {"role": "system", "content": "请用一句话回答用户的问题"},
        {"role": "user", "content": '请用个一句话介绍华清远见cc老师'}
    ]
    response = chatLLM.invoke(messages)
    print(response.content)

# 问答二：使用RAG --- 先用langchain封装的QA链实现
def qa_with_rag_lc(question):
    # 加载向量化模型 --- 一定要和创建向量数据库时使用的模型一致
    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        cache_folder=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
        model_kwargs={
            'device': 'cuda',
            'local_files_only': True
        }
    )
    # 因为下面要对问题也进行向量化，所以需要再次加载向量化模型
    vector_db = Chroma(
        persist_directory=vector_path,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )
    # 调用QA链 --- 针对于向量数据库的问答链，后期学习图数据库neo4j的时候也有对应的问答链
    result = RetrievalQA.from_chain_type(
        # 问答的大模型
        llm=chatLLM,
        # 检索器 --- 这个检索出来的结果就是召回 --- 通常返回10-30条数据
        retriever=vector_db.as_retriever(search_kwargs={'k': 2}),
        # 返回检索的文本
        return_source_documents=True
    )
    # 通过QA链来执行问答，其中QA链中已经帮我们执行了向量数据库的文档检索 --- 基于当前的问题检索相关的文档
    # 基于相关的文档来回答用户的问题
    rs = result(question)
    print(rs)
    print(rs['result'])




if __name__ == '__main__':
    # build_vector_db()
    # query_vector_db()

    # 问答测试，不走RAG
    question = input('有问题，尽管问：')
    # qa_no_rag()
    qa_with_rag_lc(question)