from langchain_community.document_loaders import TextLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_chroma import Chroma
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from langchain_community.embeddings import HuggingFaceEmbeddings

# 数据集路径
data_path = str(Path(os.path.dirname(__file__)).parent)
# 数据路径
file_path = os.path.join(data_path, 'datasets', '糖尿病.txt')
# print(file_path)

# 语义模型
model_scope = r"E:\models\split_iic"

# 存储位置
vector_path = r"E:\workspace\project_study\str_rag\自测项目尝试\chroma_test"
# 集合名称
collection_name = "tnb"
# 模型名称
embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# embedding模型存储路径
embedding_model_path = r"E:\models\paraphrase-multilingual-MiniLM-L12-v2"

# 设置向量化模型 ---目前只能选择这种方式不考虑其他加载方式
embedding_model = HuggingFaceEmbeddings(
    # 模型名称
    model_name=embedding_model_name,
    # 设置缓存路径
    cache_folder=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
    model_kwargs={
                'device': 'cuda',
                'local_files_only': True
    }
)



def build_emb_base():
    # 加载文本
    loader = TextLoader(file_path, encoding="utf-8")
    data = loader.load()
    data1 = data[0].page_content
    #  语义分割
    p = pipeline(
        task=Tasks.document_segmentation,
        model=model_scope,
        model_revision='master'
    )
    res = p(documents=data1)
    doc = res[OutputKeys.TEXT]
    # 加载文件分割对象
    test_spliter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
        separators=["", "\n", "。", "，", "？", "、", "：", "；", "！", "“", "”", "（",
            "）", "《", "》", "……", "——", "‘", "’", "·", "【", "】"],
        length_function=len,
    )
    docs = test_spliter.split_text(doc)
    # docs1 = [doc for doc in res]
    print(docs)



    # 创建向量数据库并存入数据 --- 一步到位，直接就把数据存入到了向量数据库中
    vector_test = Chroma.from_texts(
        # 数据内容
        texts=docs,
        # 选向量化模型
        embedding=embedding_model,
        # 集合名称
        collection_name=collection_name,
        # 存储位置
        persist_directory=vector_path
    )
# 加载数据库对象，看集合是否创建陈工，文档是否添加
def query_vector_test():
    vector_test = Chroma(persist_directory=vector_path, collection_name=collection_name)
    print(vector_test.get())

# 开始搭建问答链
question = '介绍一下胰岛素使用的注意事项'











if __name__ == '__main__':
    # build_emb_base()
    query_vector_test()
