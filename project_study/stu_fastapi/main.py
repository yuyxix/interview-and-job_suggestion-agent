# 导入FastAPI
import uvicorn as uv
from fastapi import FastAPI

from chat.controller.ChatController import chat_router
from chat.controller.HistoryController import history_router
# from register.controller.RegisterController import register_router
# 导入子路由对象
from users.controller.UsersController import users_router



# 生命周期
# 启动项目和关闭项目分别执行一些内容
from contextlib import asynccontextmanager
@asynccontextmanager
async def start_end_run(app):
    '''
        app：FastAPI对象
        yield 之前的内容：启动项目执行
        yield之后的内容：关闭项目执行
        如果想实现一些变量的初始化操作，可以把变量写入到app.state属性中，格式如下：
            app.state.变量名 = 初始化值
        如果某个接口需要使用，就用request 对象取出来，格式如下：
            变量名2 = request.app.state.变量名
    '''
    print('项目启动')
    yield
    print('项目关闭')

app = FastAPI(lifespan=start_end_run)

# 注册子路由
app.include_router(
    router=users_router,
    prefix='/users',  # 配置访问子路由接口的前缀，默认'',推荐写为模块的报名做区分
    tags=['users'] # 配置swaggerUI中的模块名称
)

app.include_router(
    router=chat_router,
    prefix='/chat',
    tags=['chat'],
)

app.include_router(
    router=history_router,
    prefix='/history',
    tags=['history'],
)

# app.include_router(
#     router=register_router,
#     prefix='/register',
#     tags=['register'],
# )

# 静态资源配置
from fastapi.staticfiles import StaticFiles
app.mount(
    '/static',  # 静态资源的访问前缀 --- 请求路径
    StaticFiles(directory='static'),   # 静态资源目录 --- 放行文件夹
)


# 跨域配置
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8080'],  # 允许的域名
    allow_credentials=True,  # 允许携带cookie
    allow_methods=['*'],  # 允许的请求方法
    allow_headers=['*'],  # 允许的请求头
)


# 运行fastAPI
if __name__ == "__main__":
    # 推荐的启动方法
    # 配置启动
    uv.run(
        # 启动项目的文件，即FastAPI对象所在的文件
        app='main.app', # main.py中的app对象
        host='localhost', # 配置启动的服务器地址
        port=8000, # 配置启动的服务器端口
        reload=False # 配置关闭自动重启
    )
