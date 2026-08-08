from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model=os.getenv('LLM_MODEL_NAME'),
    streaming=True
)




