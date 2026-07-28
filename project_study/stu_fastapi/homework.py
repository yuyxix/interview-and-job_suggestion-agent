# # 导入FastAPI
# import uvicorn
# from pydantic import BaseModel
# from fastapi import FastAPI, UploadFile, File, Form
# import os
# import test
# import pymysql
# from starlette.middleware.cors import CORSMiddleware
# from starlette.staticfiles import StaticFiles
#
# # 创建fastapi实例，也就是对象
# app = FastAPI()
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
# # 请求路径参数
# @app.get("/hello/{name}/{password}")
# async def say_hello(name: str, password: str):
#     return {"message": f"Hello {name} {password}"}
#
#
# # 查询参数 --- 参数以key1=value1&key2=value...形式传递过来
# # /
#
# # 分页查询，page变量表示当前数据的页码，size表示每页的数据条数，username表示查询的用户名【可能有可能无】
# @app.get('/findUsers')
# def find_user(page: int, size: int, username: str):
#     print(page, size, username)
#     return {'message': f'name: {page} size: {size}'}
#
# # 请求体  --- json数据接收
#
# # 创建连接对象
# conn = pymysql.connect(
#     # 连接数据库服务所在的ip地址
#     host='localhost',
#     # 数据库服务器运行的端口号
#     port=3306,
#     # 数据库的用户名
#     user='root',
#     # 数据库的密码
#     password='3278708004cyx',
#     # 数据库的名称
#     database='login',
#     # 连接的字符编码
#     charset='utf8'
# )
#
# # 通过账号查询数据库数据
# # 2.通过链接对象获取游标对象 --- 操作数据库的对象
# cur = conn.cursor()
# # 3.写操作数据库的命令 --- 通过账号查询数据库数据
# sql = 'select * from user'  # %变量占位符，有顺序问题
# # 4.执行SQL语句，若SQL语句中有参数，就要赋值【值放在列表里面】
# ex = cur.execute(sql)
#
# # 5.查询操作不会对数据库中的数据产生影响，不需要做事务处理
# # 查询操作得到的是数据内容，需要通过fetchall方法获取---返回值元组，每一个数据就是元组中的元组
# # 元组的数据内容值只有对应的值，没有列名 --- 按照表的结构顺序展示的
# data = cur.fetchall()
# dic = {}
# for i,j in data:
#     dic[i] = j
# account = list(dic.keys())
# pw = list(dic.values())
#
# class Login(BaseModel):
#     username: str
#     password: str
#
# @app.post('/queryParams')
# def login(username: str, password: str):
#     if username in account and password == dic[username]:
#         return {
#             'code': 200,
#             'message': '登陆成功',
#             'data': None
#         }
#     elif username not in account:
#         return {
#             'code': 500,
#             'message': '用户名错误',
#             'data': None
#         }
#     elif username in account and password != dic[username]:
#         return {
#             'code': 500,
#             'message': '密码错误',
#             'data': None
#         }
#
#
#
# # 接受文件并存储
#
# upload_path = os.path.join(os.path.dirname(__file__), 'static', 'upload')
#
# @app.post('/upload')
# def upload(file: UploadFile = File(...)):
#     # 获取文件的名字
#     filename = file.filename
#     # 项目中存储图片的时候，用时间戳作为图片的名字，防止重名
#     # 把文件写入磁盘
#     with open(os.path.join(upload_path, filename), 'wb') as f:
#         # file.file.read():获取文件中的数据内容
#         f.write(file.file.read())
#     print('写入成功！！')
#     return {'filename': 'xxx'}
#
# static_path = os.path.join(os.path.dirname(__file__), 'static')
#
# # 访问静态资源放行
# # StaticFiles(directory='static‘这里的directory就是要放行的的资源的文件夹，相当于下放权限)
# app.mount('/static', app=StaticFiles(directory=static_path), name='static')
#
# # 跨域配置
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://192.168.2.111:8000/"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#
# )
#
# # 运行fastAPI
# if __name__ == "__main__":
#     #     uvicorn.run(
#     #         'main:app',
#     #         host="0.0.0.0",
#     #         # host="192.168.2.111",
#     #         port=8000,
#     #         reload=False
#     # )
#     pass