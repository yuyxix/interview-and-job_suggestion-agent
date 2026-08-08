from ai.LLM import chatLLM

def reply(question):
    answer = chatLLM.invoke(question)
    return {
        'code': 200,
        'msg': answer.content,
        'data': None,
    }
