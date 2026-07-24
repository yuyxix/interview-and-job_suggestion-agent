"""
    modelscope下载模型步骤：
        第一步：安装库 --- 已完成
        第二步：安装
            1.命令行方式：
                modelscope download --model iic/nlp_bert_document-segmentation_chinese-base --local_dir ./dir
            2.SDK下载：
                from modelscope import snapshot_download
                model_dir = snapshot_download('iic/nlp_bert_document-segmentation_chinese-base')
"""
# 下载 modelscope download --model iic/nlp_bert_document-segmentation_chinese-base --local_dir G:\models\split_iic
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from langchain_community.document_loaders import TextLoader
import os
# 指定模型路径和模型名称
model_path = r"E:\models\split_iic"

# 获取目录根路径
# base_path = str(Path(os.path.dirname(__file__)).parent)
base_path = (os.path.dirname(os.path.dirname(__file__)))
# print(base_path)

# 拼接数据集路径
file_path = os.path.join(base_path, 'datasets', '华清远见.txt')

def txt_loader(file_path):
    # 加载TextLoader对象
    loader = TextLoader(
        file_path = file_path,  # 加载的文件路径
        encoding = 'utf-8',  # 设置编码
    )
    data = loader.load()
    return data

doc = txt_loader(file_path)
docs = doc[0].page_content
print(docs)


p = pipeline(
    task=Tasks.document_segmentation,
    model=model_path,
    model_revision='master'
)

# 把documents换成华清远见.txt中的数据
result = p(
    documents=docs
)
# OutputKeys是一个类，里面有个属性Text，表示文本
print(result[OutputKeys.TEXT])
print(result[OutputKeys.TEXT].split('\n'))