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

'''
这段代码构建了一个对话消息列表，用于传递给大语言模型：
system 消息：设定 AI 的角色为"有用的助手"，控制其行为风格
user 消息：将用户输入的问题 question 作为对话内容发送给模型
这是 OpenAI 风格的对话格式，模型会根据这两条消息生成回复。
'''
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": question}]

# invoke：非流式输出，生成回复
response = chatLLM.invoke(messages)
for chunk in chatLLM.stream(messages):
    # flush参数：缓冲区，True表示立即输出，如果为False会先保留内容，直到缓冲区满或遇到换行符才输出
    # 而Flash为True则表示立即输出，这里for循环中的chunk取出一个输出一个，从而达到流式输出的效果
    print(chunk.content, end='', flush=True)