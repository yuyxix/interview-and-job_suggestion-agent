from langchain.agents import create_agent
from state.email_state import EmailState
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from Model.my_model import MyModel


# 参数校验
class RouterResponse(BaseModel):
    flag: str = Field(..., description="意图标志")
    confidence: float = Field(..., description="置信度")


def router_node(state: EmailState):
    model = MyModel.get_local_model()
    prompt = """
        你是一个精准的意图分类器。你的唯一任务是分析用户的输入，将其归类为指定意图，并评估你对该判断的置信度。
        
        ## 🏷️ 意图类别
        1. 【SendEmail】：用户明确表达了发送、撰写、回复、转发邮件的执行动作，或提及了邮件操作（如添加附件、修改收件人等）。
        2. 【Chat】：除发邮件以外的所有其他输入，包括日常闲聊、问答咨询、情绪表达、询问邮件相关知识（如“邮箱地址是什么”、“怎么发邮件”）等。

        ## ✅ 判定法（优先级最高，与上面冲突时以本节为准）
        只问自己一个问题：用户是要我“现在就把一封邮件发出去”吗？
        - 是 → SendEmail
        - 不是（包括：闲聊、问候、感慨、提问、讨论邮件知识、问我有没有发邮件的能力、让我写文案但没说要发）→ Chat

        注意：句子里出现“邮件”两个字 ≠ SendEmail。
        没有明确收件人指向的，一律 Chat。
        只是让我“发一下”“看一下”“写一下”某个材料，但没说要发邮件的，一律 Chat。
        
        ## ⚠️ 核心规则
        - 必须且只能输出一个合法的 JSON 对象，不要包含 markdown 代码块标记（如 ```json）、解释、换行符或其他任何额外文本。
        - JSON 对象必须严格包含且仅包含两个键："flag" 和 "confidence"。
        - "flag" 的值只能是字符串 "SendEmail" 或 "Chat"。
        - "confidence" 的值必须是 0.0 到 1.0 之间的浮点数。
        
        ## 📊 置信度评分标准
        - 0.9 - 1.0：意图极其明确，无任何歧义（如“帮我给张三发封邮件”）。
        - 0.7 - 0.89：意图较明确，但存在轻微模糊或省略（如“发给项目组”未提“邮件”二字，但上下文可推断）。
        - 0.5 - 0.69：意图勉强可判断，但存在明显歧义或信息缺失（如“那个东西发一下”）。
        - < 0.5：几乎无法判断，建议降级为 Chat 并追问用户。
        
        ## 📝 输出示例
        
        用户：帮我给张三发一封邮件，主题是下周的项目进度汇报
        助手：{"flag": "SendEmail", "confidence": 0.98}
        
        用户：今天天气真不错啊
        助手：{"flag": "Chat", "confidence": 0.99}
        
        用户：写一封邮件回复李四，告诉他会议改到下午三点
        助手：{"flag": "SendEmail", "confidence": 0.95}
        
        用户：请问公司的公共邮箱地址是多少？
        助手：{"flag": "Chat", "confidence": 0.95}
        
        用户：你好
        助手：{"flag": "Chat", "confidence": 0.99}
        
        用户：你能帮我发邮件吗？
        助手：{"flag": "Chat", "confidence": 0.95}

        用户：邮件怎么写才正式？
        助手：{"flag": "Chat", "confidence": 0.98}
        
        用户：嗯嗯好的
        助手：{"flag": "Chat", "confidence": 0.85}
        """

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=prompt,
        response_format=RouterResponse
    )
    msg = {'messages': [{'role': 'user', 'content': state['messages'][0].content}]}
    # 获取结果
    rs = agent.invoke(msg)
    # 把响应结果转换为字典
    json = rs['structured_response'].model_dump()
    # 定义result，即ai返回的内容
    ai_msg = f'\n意图节点识别成功：\n 意图：{json["flag"]} \n 置信度：{json["confidence"]}'
    # 只返回当前节点修改的状态信息
    return {
        'messages': [AIMessage(content=ai_msg)],
        'flag': json['flag'],
        'confidence': json['confidence']
    }
