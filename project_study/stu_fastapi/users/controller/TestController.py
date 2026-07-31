import time
import json
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel, Field

from users.service import TestService

# 创建子路由对象
users_router = APIRouter()

# 定义了一个函数 ---接口函数
# 配置子路由接口的访问路径 --- 并不是最终的接口访问路径
@users_router.get('/sayHello')
def say_hello():
    return {
        'msg': 'hello'
    }


'''
    方式一 查询参数：get 请求 + key = value 数据
        直接使用形参接收，形参的名字需要和key 相同，否则接收不到数据
'''

@users_router.get('/getParams')
def get_params(username: str, password: str):
    print(f'接收到的数据为：username={username}, password={password}')
    return {
        'code': 200,
        'msg': 'success',
        'data': {
            'username': username,
            'password': password
        }
    }

'''
    方式二 路径参数：get 请求 + 参数直接在请求路径后面(没有key只有value)
    需要在接口的请求路径定义中，定义变量{变量占位}，然后在接口方法中定义和占位变量相同的名字来接收，有顺序问题
    通常情况下用于查询，删除操作

'''

@users_router.get('/getParamsTwo/{username}/{password}')
def get_params_two(username: str, password: str):
    print(f'接收到的数据为：username={username}, password={password}')
    return {
        'code': 200,
        'msg': 'success',
        'data': {
            'username': username,
            'password': password
        }
    }

'''
两种方式都能用，表面区别只体现在代码和URL地址上
但实际上还包含了一种意图区别：
    路径参数强调指定浏览某个参数的页面
    查询参数强调查询某个key是否存在对应的value
'''

'''
方法三：post请求 + json格式数【application/json】
    需要定义一个类来接收， 类的属性的名字必须和json数据中key相同，比如：
        json --- {'username: 'admin', 'password': '111'}
        类 --- username: str password: str
'''

# 定义接受数据的类 --- 直接继承BaseModel即可
class TestClass(BaseModel):
    # 定义属性 --- Field(..., title='用户名') 关于这个属性的说明
    usersname: str = Field(..., title='用户名')
    password: str = Field(..., title='密码')

@ users_router.post('/postParams')
def post_params(testClass: TestClass):
    print(f'接收到的数据为：{testClass}')
    print(testClass.usersname, testClass.password)
    return {
        'code': 200,
        'msg': 'success',
        'data': testClass
    }

'''
    方式四：post 请求 + 文件 file
        file类型的数据，必须用post请求
        通过接口形参来接收，形参用UploadFile类来接收
        file文件以外的数据可以封装在Form中，如username: str = Form(...)就是接受变量username
'''
@users_router.post('/postFile')
def post_file(file: UploadFile = File(...), username: str = Form(...)):
    # 取出文件的名字
    filename = file.filename
    suffix = str(int((time.time()))) + '.' + filename.split('.')[-1]
    # 存储地址 + 文件名字
    save_path = r'E:\workspace\project_study\stu_fastapi\static\upload\\' + suffix
    # 存储文件
    with open(save_path, 'wb') as f:
        f.write(file.file.read())
    return {
        'code': 200,
        'msg': 'success',
        'data': ''
    }

'''
流式输出：方案一
    在fastapi中，通过设置接口的方法的返回值就可以实现流式输出
StreamingResponse:
    在fastapi中，通过设置接口方法的返回值就可以实现流式输出
    参数：
        1.content：一个迭代器(生成器)对象，直接通过yield作为函数返回值即可创建出来迭代器(生成器)对象
        2.media_type：xxxx
'''
from starlette.responses import StreamingResponse
'''
    流式输出 方案一： 客户端需要使用fetch请求方式 服务器直接把结果返回值返回，不做任何处理
        优点：服务器代码简单
        缺点：客户端代码非常难写
'''

@users_router.get('/testStream')
def test_stream():
    # 假设模型的返回值为0-9
    def generator():
        for i in range(10):
            # 返回一个生成器对象
            yield str(i)
            time.sleep(0.03)
    return StreamingResponse(
        content=generator(),
        media_type='text/plain; charset = utf-8'
    )

'''
    流式输出 方案二：客户端使用SSE请求，服务器必须把数据包装成data：数据内容\n\n字符串格式，否则报错
        服务器中通常把数据内容转为json格式返回，便于客户端处理，并且需要告诉客户端数据输出什么时候结束【需要一个标识符】
'''

@users_router.get('/testStreamSSE')
def test_stream_sse():
    # 假设大模型的返回值
    result = '你好，有什么可以帮你的吗？'
    # 假设模型的返回值为0-9
    def generator():
        for i in result:
            # 返回一个生成器对象
            yield f'data: {json.dumps({'content': i})}\n\n'
            time.sleep(0.1)

        # 返回数据内容结束
        yield f'data: {json.dumps({'content': '[DONE]'})}\n\n'
    return StreamingResponse(
        content=generator(),
        media_type='text/event-stream,'
    )

# 结合llm达到流式输出
@users_router.get('/LLMstreaming/{question}')
def llm_streaming(question: str):
    # # 假设大模型的返回值
    # question = question
    # result = answer(question)
    # # 假设模型的返回值为0-9
    # def generator():
    #     for i in result:
    #         # 返回一个生成器对象
    #         yield f'data: {json.dumps({'content': i})}\n\n'
    #         time.sleep(0.1)
    #
    #     # 返回数据内容结束
    #     yield f'data: {json.dumps({'content': '[DONE]'})}\n\n'

    # 在service层就完成了流式输出

    # 处理数据为sse需要的格式
    def generator():
        for item in TestService.answer(question):
            yield f'data: {json.dumps({'content': item})}\n\n'
        yield f'data: {json.dumps({'content': '[DONE]'})}\n\n'
    return StreamingResponse(
        content=generator(),
        media_type='text/event-stream,'
    )


'''
    配置一个访问a.html页面的请求路径

'''
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

# 创建模板对象
templates = Jinja2Templates(directory='templates')
@users_router.get('/goA')
def go_a(request: Request): # request是请求对象，伴随着客户端访问服务器的时候产生的，可以获取客户端传递过来的内容等
    return templates.TemplateResponse(request=request, name='a.html')