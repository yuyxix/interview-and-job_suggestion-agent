from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 测试数据 --- 项目中的数据来源于数据集【各种类型情况都有】
text = """
华清远见2004年成立于北京中关村，12年来始终专注于嵌入式及移动开发专业人才培养，“做良心教育，做专业教育，做受人尊敬的职业教育”是华清远见一直坚持的核心发展理念。培训内容主要包括嵌入式系统开发，Android开发，物联网开发、HTML5开发、UI设计。从短期高端到长期就业课程培训，再到产品研发，凭借专业的课程内容、强大的师资团队以及先进的研发技术受到客户和学员的好评。迄今已有超过10万名学员从华清远见走出。
华清远见研发实力强大。拥有10余种实训套件与智能产品，100余套自主研发实验设备。同时与众多高校进行实验室共建合作，目前已有超过1100所高校1100多个实验室选择了我们。华清远见拥有众多高端培训课程，每类课程均有独特的教学模式。不同于其他机构，华清远见的培训课程不仅限于理论知识，还有丰富多样的实战项目贯穿其中。从研发到培训，全面提升学员技术水平。
华清远见拥有一支非常强大的师资团队。近200余名讲师投身于研发当中。每位讲师均是从事IT行业多年的资深人士，并有着丰富的项目开发经验。在学员培训过程中实时答疑解惑。
华清远见成都中心设有教学部、教务部、市场部等多个部门，其中教学部根据专业方向分为AI教学部和嵌入式教学部，分别负责不同技术领域的人才培养与课程教学工作。AI教学部主要负责人工智能、大数据等相关课程的教学与项目实践，致力于培养具备实际开发能力的AI技术人才。
cc老师是AI教学部的一名讲师，拥有丰富的人工智能领域教学经验，在课程讲授与项目指导过程中深受学员欢迎。
"""

# 加载分词器对象
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    separators=["\n\n", "\n", "。", "，", " "],
)

# 加载数据
data = text_splitter.split_text(text)

# 把data中的数据转为Document对象，满足Chroma.from_documents存入格式
documents = [Document(page_content=item, metadata={'source': '华清远见.txt'}) for item in data]

# 加载向量化模型 --- 一定要和创建向量化数据库时使用的模型一致
embedding_model = HuggingFaceEmbeddings(
    model_name=r'E:\models\paraphrase-multilingual-MiniLM-L12-v2',
    model_kwargs={
        'device': 'cuda',
        'local_files_only':  True
    }
)
# 存入到向量数据库中
try:
    Chroma.from_documents(
        # 数据文本
        documents=documents,
        # 向量化模型
        embedding=embedding_model,
        # 存储位置
        persist_directory='./test_db',
        # 检索方式为余弦相似度
        collection_metadata={"hnsw:space": "cosine"},
        # 集合名称
        collection_name="hqyj",
    )
    print("数据存入成功")
except Exception as e:
    print(f"数据存入失败：{e}")
