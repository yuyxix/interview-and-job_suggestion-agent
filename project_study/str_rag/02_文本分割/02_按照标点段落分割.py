# 导包
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader


# 设置文件访问路径
base_path = (os.path.dirname(os.path.dirname(__file__)))
file_path = os.path.join(base_path, 'datasets', '糖尿病.txt')

# 文本加载器
loader = TextLoader(file_path=file_path, encoding='utf-8')
data = loader.load()
text = data[0].page_content


# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    # read 函数读取这个文件的内容，返回一个字符串
    text = f.read()
    # 去点\n
    text = text.replace('\n', '')
    # print(text)
# 加载文件分割的对象
text_splitter = RecursiveCharacterTextSplitter(
    # 块的大小
    chunk_size=300,
    # 块的重叠程度
    chunk_overlap=50,
    # 分隔符 --- 写在前面的分隔符的优先级最高
    separators=["", "\n", "。", "，", "？", "、", "：", "；", "！", "“", "”", "（",
            "）", "《", "》", "……", "——", "‘", "’", "·", "【", "】"],
    # 计算块长度
    length_function=len,
)

# 通过分割对象对文本进行分割
results = text_splitter.split_text(text)

# 遍历
for item in results:
    print(item)
    print('=' * 50)