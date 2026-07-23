from langchain_community.document_loaders import JSONLoader
import os
from pathlib import Path

base_path = str(Path(os.path.dirname(__file__)).parent)

# 拼接数据集路径
file_path = os.path.join(base_path, 'datasets', 'Chinese.json')

def json_loader(file_path):
    '''
    这段代码定义了一个 jq 表达式，用于从 JSON 数组中提取并格式化每条数据：
    .[]：遍历 JSON 数组中的每个元素
    .instruction、.input、.output：分别提取每个元素的三个字段
    用 + 拼接为格式化字符串，字段间用 \n 换行分隔
    例如：
    instruction: 请回答以下问题
    input: 你好
    output: 你好！

    :param file_path:
    :return:
    '''

    loader = JSONLoader(
        file_path = file_path,
        jq_schema = '.[] | "instruction:" + .instruction + "\\n" + "input:" + .input + "\\n" + "output:" + .output'
    )
    data = loader.load()
    return data

if __name__ == '__main__':
    js = json_loader(file_path)
    print(js)
    for item in js:
        print(item.page_content)