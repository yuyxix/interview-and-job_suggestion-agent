from ai.LLM import chatLLM

def answer(question):
    '''
        方案一：假流式输出 --- 等待LLM输出了所有结果然后再返回
    '''
    # messages = [
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": question},
    #     ]
    # response = chatLLM.invoke(messages)
    # return response.content
    '''
        方案二：流式输出
    '''
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
        ]
    for chunk in chatLLM.stream(messages):
        # 用if判断来过滤空白字符
        if chunk.content:
            yield chunk.content



if __name__ == '__main__':
    for chunk in answer('hello'):
        print(chunk)
