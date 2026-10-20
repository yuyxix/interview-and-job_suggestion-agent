from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 读取配置文件
load_dotenv()


# 基于单例模式的模型封装
class MyModel:
    # 定义私有属性
    # 在python的单例模式中，对象创建通过私有属性的方式来赋值
    _model = None
    # 定义本地模型私有属性
    _local_model = None
    # 定义静态函数
    # 这种封装都应该定义静态函数，原因：
    # 1. 如果不用静态函数，_model = None容易被其它对象传入的self修改，用静态方法则确保与参数无关，只能通过函数修改成特定的情况
    # 2. MyModel.get_model() 一眼就能看出"这是获取 MyModel 单例的方法"，代码自解释，代码更清晰
    # 3. 类的定义和它的单例获取逻辑放在一起，符合面向对象的设计原则，这种思想要尽可能去除感受和理解
    # 4. 在生产环境中，后续用到这个模型都走这个实例，不会产生新的开销
    @staticmethod
    def get_model():
        # 判断_model是否为空
        if MyModel._model is None:
            # 创建模型
            MyModel._model =ChatOpenAI(
                model=os.getenv("MODEL_NAME"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv('BASE_URL'),
                streaming=True,
            )
        return MyModel._model
    @staticmethod
    def get_local_model():
        if MyModel._local_model is None:
            # 创建模型
            MyModel._local_model =ChatOpenAI(
                model=os.getenv("MODEL_LOCAL_NAME"),
                api_key='ollama',
                base_url=os.getenv("LOCAL_URL"),
                streaming=True,
            )
        return MyModel._local_model

if __name__ == '__main__':
    model = MyModel.get_model()
    rs = model.invoke('你好')
    print(rs)