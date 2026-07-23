"""
json:
    1. 满足键值对格式的字符串
    {key1: value1, value2: value2}
    2. Json字符串需要是双引号
"""

import json
if __name__ == '__main__':
    # 定义一个字典
    data_dict = {
        "name" : "张三",
        "age" : 18,
        "is_student" : True
    }

# 字典转Json

# json.dumps 在 Python 3 中没有 encoding 参数。
r""" 要控制中文等非 ASCII 字符的输出，应使用 ensure_ascii 参数：
    ensure_ascii=True（默认）：中文会被转义为 \uXXXX 形式
    ensure_ascii=False：中文原样输出，不会被转义
"""


json_str = json.dumps(data_dict, )
print(json_str)
print(type(json_str))
for i in json_str:
    print(i)

