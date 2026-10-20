import os
from dotenv import load_dotenv
import requests

load_dotenv()

# 根据地点获取地图编码工具
def get_code(address):
    # 定义url
    url = 'https://restapi.amap.com/v3/geocode/geo?parameters'
    # 定义参数
    params = {
        "key": os.getenv("AMAP_API_KEY"),
        "address": address,
    }
    # 定义请求
    rs = requests.get(
        url=url,
        params=params
    )
    # 数据类型转换
    data = rs.json()
    location = data['geocodes'][0]['location']
    return location

if __name__ == "__main__":
    print(get_code("成都"))
