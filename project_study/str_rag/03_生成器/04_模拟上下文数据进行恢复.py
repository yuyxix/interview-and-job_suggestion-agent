from langchain_openai import ChatOpenAI
import os

# 创建一个ChatOpenAI实例，即配置要调用的模型以及api还有其他的相关配置
chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-max-preview",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
    streaming=True
)

question = input('有问题，尽管问：')

# 模拟上下文 ---后期来源于向量数据库中查询出来的数据
context = ("cc是一名华清远见成都中心的AI讲师，他擅长用Python开发AI模型")

# 拼接问题与上下文 ---后期使用提示词来完成
content = "请根据上下文信息：\n" + context + "\n回答用户的问题：\n" + question

messages = [
    {"role": "system", "content": "请用一句话回答用户的问题"},
    {"role": "user", "content": content}]

# invoke：非流式输出，生成回复
response = chatLLM.invoke(messages)
print(response.content)