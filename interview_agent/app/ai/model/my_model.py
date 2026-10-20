from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from vosk import Model

# 读取配置文件
load_dotenv()


# 基于单例模式的模型封装
class MyModel:
    # 定义私有属性
    # 在python的单例模式中，对象创建通过私有属性的方式来赋值
    _model = None
    # 定义本地模型私有属性
    _local_model = None
    # 定义语音模型
    _vosk_model = None

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
                stream_usage=True,
                # 关闭思考模式
                extra_body={
                    'enable_thinking': False
                }
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
                # langchain_openai 必须显式发 stream_options={"include_usage": True} 才会去解析 token 用量，这个开关由 stream_usage 控制
                stream_usage=True,
            )
        return MyModel._local_model

    @staticmethod
    def get_vosk_model():
        # 判断_model是否为空
        if MyModel._vosk_model is None:
            # 创建模型
            model_path = os.getenv("VOSK_PATH")
            # 加载模型
            MyModel._vosk_model = Model(model_path=model_path)
        return MyModel._vosk_model


if __name__ == '__main__':
    model = MyModel.get_model()
    rs = model.invoke('你好')
    print(rs)