import time

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import os



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

def qa_with_gar_lc(question):
    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        cache_folder=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
        # 执行本地模型
        model_kwargs={
            'device': 'cuda',
            'local_files_only': True
        }
    )

    # 加载向量数据库对象
    vector_db = Chroma(
        collection_name=collection_name,
        persist_directory=vector_path,
        embedding_function=embedding_model
    )

    # 获取检索器
    retriever = vector_db.as_retriever(search_kwargs={"k": 2})
    print(retriever)
    # 设置大模型回复提示词 --- 属于系统提词
    template = """
    你是一个基于知识库的智能助手。

    请结合检索到的知识内容回答用户问题：
    - 仅使用提供的知识内容作为依据；
    - 不确定的信息不要推测；
    - 对无法回答的问题说明原因；
    - 输出清晰、准确、简洁的答案。
    - 输出结果的时候不允许输出根据提供的参考资料这样的内容
    - 输出结果时，若没有参考的上下文信息，请给出一个友好的回复消息    
    知识内容：
    {context}
    
    用户问题：
    {question}
    
    请生成最终答案：
    """

    # 创建提示词对象
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # 打印召回结果
    def print_docs(docs):
        print('检测到的文档内容：')
        for doc in docs:
            print(f'docs:{docs}')
            print(f'doc:{doc}')
            print(f'doc中的文本:{doc.page_content}')
            print('=' * 80)
        # 返回索引结果给后续使用
        return docs

    # RunnableParallel:并行执行多个 Runnable
    '''
    例如：
    RunnableParallel(
            {
                'a': 函数A
                'b': 函数B
            }
    当我们向本代码后面一样，result = qa_chain.invoke(question)，用invoke方法往qa_chain中传入一个参数时
    这就表明question作为参数传入了RunnableParallel中,并同时作为参数交给A和B函数处理
    '''


    qa_chain = (

        RunnableParallel(
            {
                # 下面的invoke方法接受的参数此时作为参数传给了retriever作为参数进行召回，这里还将召回结果作为参数传给了print_docs函数
                # 在 LangChain 中，retriever 的召回结果默认是：List[Document] 类型
                "context": retriever | RunnableLambda(print_docs),
                "question": RunnablePassthrough(), # 透明传递，直接使用question变量的值【不做任何更改】

            }
        )
        | prompt # 提示词 --- |表示管道运算符
        | chatLLM # 大模型
        | StrOutputParser() # 将chatLLM输出的结果转为字符串输出

    )

    # 调用QA链
    result = qa_chain.invoke(question)
    print('输出结果为：')
    for item in result:
        print(item)
        # 伪流式输出效果
        time.sleep(0.05)



if __name__ == '__main__':
    # 问答测试
    question = input('请输入问题：')

    qa_with_gar_lc(question)