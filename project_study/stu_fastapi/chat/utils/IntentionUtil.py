import json
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama

load_dotenv()

def intention_recognition(question):
    llm = ChatOllama(
        model=os.getenv('OLLAMA_MODEL_NAME'),
        base_url=os.getenv('OLLAMA_BASE_URL')
    )

    intention_prompt = """
        你是一个专业的法律领域意图识别专家。你的任务是判断用户的输入是否包含【法律相关】内容。

        # Definition: 什么是"法律相关"
        包括但不限于以下范畴：
        1. 法律法规咨询（刑法、民法、劳动法、婚姻法、知识产权等）
        2. 合同纠纷、违约责任、债务追讨
        3. 诉讼、仲裁、行政复议、报案流程
        4. 律师咨询、法律援助、公证遗嘱
        5. 交通事故/工伤/医疗事故的赔偿责任认定
        6. 消费者权益保护、维权投诉
        7. 公司合规、股权架构、破产清算

        # Definition: 什么是"不相关"
        1. 纯情感倾诉且未提及任何权益/纠纷/规则
        2. 纯粹的道德伦理讨论（不涉及法律评价）
        3. 日常生活闲聊、技术问题、娱乐八卦
        4. 虽然涉及冲突但明确属于私人恩怨且无法律诉求

        # Output Format
        仅输出一个JSON对象，不要包含任何其他解释文字：
        {
            "is_legal": True/False,
            "confidence": "high/medium/low",
        }

        # Examples
        User: "我和房东签了合同但他不退押金怎么办"
        Assistant: {"is_legal": true, "confidence": "high"}

        User: "今天心情好差，感觉活着没意思"
        Assistant: {"is_legal": false, "confidence": "high"}

        User: "Python怎么读取Excel文件"
        Assistant: {"is_legal": false, "confidence": "high"}

        User: "邻居半夜唱歌太吵了"
        Assistant: {"is_legal": true, "confidence": "medium"}
    """

    res = llm.invoke([
        {'role': 'system', 'content': intention_prompt},
        {'role': 'user', 'content': question}
    ])
    return json.loads(res.content)

if __name__ == '__main__':
    print(intention_recognition('你好'))