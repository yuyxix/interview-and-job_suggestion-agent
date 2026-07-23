from langchain_community.document_loaders import TextLoader
import os
from pathlib import Path

# 获取目录根路径
# base_path = str(Path(os.path.dirname(__file__)).parent)
base_path = (os.path.dirname(os.path.dirname(__file__)))
# print(base_path)

# 拼接数据集路径
file1_path = os.path.join(base_path, 'datasets', '华清远见.txt')
file2_path = os.path.join(base_path, 'datasets', '糖尿病.txt')

def txt_loader(file_path):
    # 加载TextLoader对象
    loader = TextLoader(
        file_path = file_path,  # 加载的文件路径
        encoding = 'utf-8',  # 设置编码
    )
    data = loader.load()
    return data


# main + enter
if __name__ == '__main__':
    txt1 = txt_loader(file1_path)
    print(txt1)
    print('=' * 50)
    txt2 = txt_loader(file2_path)
    print(txt2)