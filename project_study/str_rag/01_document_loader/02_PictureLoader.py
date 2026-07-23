# 要识别图中的文件需要借助ORC技术
from langchain_community.document_loaders import UnstructuredImageLoader
import unstructured_pytesseract.pytesseract as pytesseract
import os
from pathlib import Path

pytesseract.tesseract_cmd = r"D:\Program Files\tesseract-ocr\tesseract.exe"


# 获取目录根路径
base_path = str(Path(os.path.dirname(__file__)).parent)

# 拼接数据集路径
file_png_path = os.path.join(base_path, 'datasets', '黑神话.png')
file_jpeg_path = os.path.join(base_path, 'datasets', 'image.jpeg')

def picture(file_path):
    loader = UnstructuredImageLoader(
        file_path = file_path,
        mode = 'elements',
        language = ['chi_sim']
    )
    data = loader.load()
    return data


if __name__ == '__main__':
    file1 = picture(file_png_path)
    for item1 in file1:
        print(f'黑神话：{item1}')
    print(f'黑神话：{file1}')
    print('=' * 50)
    file2 = picture(file_jpeg_path)
    for item2 in file2:
        print(f'image：{item2}')
    print(f'黑神话：{file2}')