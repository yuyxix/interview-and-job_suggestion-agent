# 导入FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form
import os
import test
import pymysql
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from users.controller.UsersController import api_router


# 创建fastapi实例，也就是对象
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# 请求路径参数
@app.get("/hello/{name}/{password}")
async def say_hello(name: str, password: str):
    return {"message": f"Hello {name} {password}"}

# 引入users模块的子路由
'''
    include_router 方法参数：
        1. router：引入子路由 --- 子路由的名字 APIRouter对象的名字
        2. prefix：访问子路由的时候添加在前面的前缀
        3. tags：在swaggerUI中分组的名字
'''
app.include_router(api_router, prefix='/users', tags=['users'])


# 运行fastAPI
if __name__ == "__main__":
        uvicorn.run(
            'main:app',
            host="0.0.0.0",
            # host="192.168.2.111",
            port=8000,
            reload=False
    )
