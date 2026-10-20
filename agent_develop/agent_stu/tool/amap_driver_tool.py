from langchain_core.tools import tool
from util.geocode_util import get_code
from tool.schema.amap_driver_shcema import AmapDriverParams
from dotenv import load_dotenv
import os
import requests

load_dotenv()

@tool(
    name_or_callable="driver_tool",
    args_schema=AmapDriverParams
)
def driver_tool(start_location: str, end_location: str):
    """
    查询用户输入的起点和终点之间的出发路线
    """
    try:
        # 查询地理编码
        start = get_code(start_location)
        end = get_code(end_location)
        url = 'https://restapi.amap.com/v5/direction/driving?parameters'
        params = {
            'key': os.getenv('AMAP_API_KEY'),
            'origin': start,
            'destination': end
        }
        rs = requests.get(url=url, params=params).json()
        route = rs['route']['paths']
        data = {}
        for i in range(len(route)):
            data[f'path{i+1}'] = route[i]
        return data

    except Exception as e:
        print(f'汽车路线查询异常:{e}')
        return "汽车路线查询失败"

if __name__ == '__main__':
    driver_tool.invoke({
        'start_location': '成都q',
        'end_location': '绵阳'
    })
