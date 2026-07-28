import os

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from FlagEmbedding import FlagReranker

# 加载向量化模型
embedding_model = HuggingFaceEmbeddings(
    model_name=r"E:\models\paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={
        "device": "cuda",
        "local_files_only": True,
    },

)
# 加载LLM
chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-max-preview",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
    streaming=False
)

# 加载重排序模型

reranker = FlagReranker(
    model_name_or_path=r"E:\models\bge-reranker-large_v1",
    use_fp16=True
)

# 查询问题
question = "华清远见成都中心有哪些部门？"
"""
    问题【用户输入，客户端】 --->  目的【基于用户的问题生成回答】
    RAG 流程：
        1、让LLM如何来生成回复【提示词】
        2、提示词：需要告诉模型上下文内容是什么，问题是什么，以及生成回复时的规则
        3、为了得到上下文信息，这里需要得到向量数据库的检索器对象
        4、构造langchain链 --- 管道运算符
"""
# 提示词文本内容
template = """
    你是一个基于知识库的AI助手。请根据RAG检索内容回答用户问题。
    规则：
        - 仅基于提供的知识回答，不使用外部知识补充。
        - 检索内容不足时，说明信息不足，不要猜测。
        - 优先提炼关键答案，避免冗长解释。
        - 保持回答自然、简洁、有帮助。
        - 输出结果的时候，不允许输出根据提供的参考资料这样的内容
        - 输出结果的时候，如果没有参考的上下文信息，请给出一个友好的回复信息
    参考资料：
        {context}
    问题：
        {question}
    答案：
"""

# 创建提示词对象
prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# 创建检索器对象
vector_db = Chroma(
    persist_directory=r"E:\workspace\project_study\str_rag\06_langchian操作chromadb\test_db",
    embedding_function=embedding_model,
    collection_name="hqyj",
)
retriever = vector_db.as_retriever(search_kwargs={"k": 5})
print(retriever)
# retrieved_docs = retriever.invoke(question)
# print(retrieved_docs)

# 打印召回结果，对召回结果进行重排序
def print_doc(docs):
    for doc in docs:
        print(doc)
    return docs

def Reranker(docs):
    rerank_input = [(question, doc.page_content) for doc in docs['context']]
    print(rerank_input)
    scores = reranker.compute_score(rerank_input)
    return scores

# 创建langchain链
qa_chain = (
    RunnableParallel(
        {
            'context': retriever | RunnableLambda(print_doc),
            'question': RunnablePassthrough()
        }
    )
    | RunnableLambda(Reranker)
    # | prompt
    # | chatLLM
    # | StrOutputParser()
)

# 测试
reply = qa_chain.invoke(question)
print(reply)

