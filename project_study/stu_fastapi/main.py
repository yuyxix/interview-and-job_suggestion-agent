# 导入FastAPI
from fastapi import FastAPI

# 创建fastapi实例，也就是对象
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
