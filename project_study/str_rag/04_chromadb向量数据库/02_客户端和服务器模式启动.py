"""
    chroma run --path 数据存储路径 --host 0.0.0.0 --port 9000
    --path：数据存储路径
    --host：服务器地址
    --port：服务器端口
"""

import chromadb


# 客户端/服务器模式
def client_server_mode():
    # 连接到正在运行的 Chroma 服务器
    client = chromadb.HttpClient(host='localhost', port=9000)
    print(client)
