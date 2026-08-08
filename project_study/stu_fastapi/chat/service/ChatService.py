from langchain_core.documents import Document

from ai import LoadChroma, LLM, LoadRerankerModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

from chat.dao import ChatDao
from chat.dao.ChatDao import delete_history
from chat.service import HistoryService
from chat.utils import IntentionUtil, BM25Util
from chat.utils import RRFUtil
def chat(question, historyId):
    # 如果historyId=0，表示一个新对话
    if historyId == 0:
        history = []
    else:
        # 查询对话记录 --- 没有考虑只查询最新的几条记录
        history = HistoryService.conversation_log(historyId)['data']
    # 使用一个小模型来做意图识别,根据结果来判断是否走RAG
    is_legal = IntentionUtil.intention_recognition(question)['is_legal']
    # 加载LLM
    llm = LLM.chatLLM

    if not is_legal:
        history.append({'role': 'user', 'content': question})
        for chunk in llm.stream(history):
            if chunk.content:
                yield chunk.content
        return

    # 加载重排序模型
    reranker = LoadRerankerModel.load_rerank_model()

    # 提示词文本内容
    template = """
        你是一个基于知识库的AI助手。请根据RAG检索内容回答用户问题。
        规则：
            - 仅基于提供的知识回答，不使用外部知识补充。
            - 检索内容不足时，说明信息不足，不要猜测。
            - 优先提炼关键答案，避免冗长解释。
            - 保持回答自然、简洁、有帮助。
            - 输出结果的时候，不允许输出根据提供的参考资料这样的内容
            - 输出结果的时候，如果没有参考的上下文信息，请给出一个友好的回复信息
        历史记录：
            {history}
        参考资料：
            {context}
        问题：
            {question}
        答案：
    """

    # 创建提示词对象
    prompt = PromptTemplate(
        template=template,
        input_variables=["history", "context", "question"]
    )
    vector = LoadChroma.load_chroma_con()


    # 打印召回结果，对召回结果进行重排序
    # def print_doc(docs):
    #     print(f'召回的结果有:{docs}')
    #     for doc in docs:
    #         print(doc.page_content)
    #     return docs

    def retriever_func(query):
        # 向量检索
        vector_result = vector.as_retriever(search_kwargs={"k": 10})
        em_retriever = vector_result.invoke(query)
        em_retriever_result = {doc.id: doc.page_content for doc in em_retriever}
        em_rrf_result = RRFUtil.rrf_util(em_retriever_result)

        # BM25检索
        bm_retriever_result = BM25Util.BM25_retriever(vector, query)
        bm_rrf_result = RRFUtil.rrf_util(bm_retriever_result)
        # rrf算法融合
        retriever_result = {}
        for i in em_rrf_result.keys():
            if i not in bm_rrf_result:
                retriever_result.update({em_retriever_result[i]: em_rrf_result[i]})
        for j in bm_rrf_result.keys():
            if j not in em_rrf_result:
                retriever_result.update({bm_retriever_result[j]: bm_rrf_result[j]})
        for i in em_rrf_result.keys():
            for j in bm_rrf_result.keys():
                if i == j:
                    rrf_score = em_rrf_result[i] + bm_rrf_result[j]
                    retriever_result.update({em_retriever_result[i]: rrf_score})
                    # 字典无法直接排序，但是可以用items方法将字典中的元素以元组的形势一对对的放入列表
        retriever_result = sorted(retriever_result.items(), key=lambda x: x[1], reverse=True)
        print(f'rrf算法融合结果：{retriever_result}')
        for i in retriever_result:
            n = 1
            print(f'文档{n}: {i[0]} 得分：{i[1]}')
            n += 1
        # 转为Document对象
        retriever_result = [Document(page_content=i[0], metadata={'score': i[1]}) for i in retriever_result]
        return retriever_result

    def Reranker(docs):
        print('开始进行重排序...')
        rerank_input = [(question, doc.page_content) for doc in docs['context']]
        scores = reranker.compute_score(rerank_input)
        context = [doc.page_content for doc in docs['context']]
        scores_list = list(zip(scores, context))
        scores_list.sort(key=lambda x: x[0], reverse=True)
        score_result = [doc for score, doc in scores_list[:3]]
        print(score_result)
        print('重排序的结果为：')
        for item in range(len(score_result)):
            print(f'【来源{item + 1}】 {score_result[item]}')
        return {
            'context': score_result,
            'question': question,
            'history':  history
        }

    # 创建langchain链
    qa_chain = (
        RunnableParallel(
            {
                'context': RunnableLambda(retriever_func),
                'question': RunnablePassthrough(),
                'history': RunnableLambda(lambda _:  history)
            }
        )
        | RunnableLambda(Reranker)
        | prompt  # 提示词
        | llm  # 大模型对象
        | StrOutputParser()  # 把llm输出的结果转为字符串输出
    )
    for chunk in qa_chain.stream(question):
        yield chunk


def save_conversation_result(ConversationEntity):
    username = ConversationEntity.username
    question = ConversationEntity.question
    answer = ConversationEntity.answer
    parent_id = ConversationEntity.parentId

    # 存储
    history_id = ChatDao.save_conversation_result(username, question, answer, parent_id)
    if history_id != 0:
        return {
            'code': 200,
            'msg': '保存成功',
            'data': None,
        }
    return {
        'code': 500,
        'msg': '保存失败',
        'data': None,
    }


def delete_conversation_history(historyId):
    delete_history(historyId)
    result = ChatDao.delete_history_tool(historyId)
    print(result)
    if len(result) == 0:
        return {
            'code': 200,
            'msg': '删除成功',
            'data': None,
        }
    return {
        'code': 500,
        'msg': '删除失败',
        'data': None,
    }


if __name__ == '__main__':
    question = '警方接到家庭暴力案件的处理'
    for chunk in chat(question, 14):
        print(chunk)

