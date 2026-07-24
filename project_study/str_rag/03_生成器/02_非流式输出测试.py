from langchain_openai import ChatOpenAI
import os

chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-max-preview",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
    streaming=False
)

question = input('有问题，尽管问：')
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": question}]

# invoke：非流式输出，生成回复
response = chatLLM.invoke(messages)
print(response.content)