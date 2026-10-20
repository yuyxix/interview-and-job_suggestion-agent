from app.ai.agent.multi_agent.state.exam_state import ExamState
from app.ai.tools.mysql_tool import mysql_tool
import ast
from langchain_core.messages import AIMessage
"""
    出题节点，随机抽取一道未出过的题目
"""


def question_node(state: ExamState):
    # 课程名称
    course = state['course']
    # 题目数量
    num = state['total']
    # 查询题目列表
    question_list = state.get('question', [])
    # 获取标准答案列表
    answer_list = state.get('sure_answer', [])
    # 获取当前题目号
    current = state.get('current_index', 0)+1
    # 判断题目列表中是否有数据
    if len(question_list) > 0:
        rs = ','.join([str(i['id']) for i in question_list])
        sql = f'select * from question_bank where question_subject="{course}" and question_id not in ({rs}) order by RAND() desc limit 1'
    else:
        sql = f'select * from question_bank where question_subject="{course}" order by RAND() desc limit 1'
    # 调用mysql工具
    rs = mysql_tool.invoke({'sql': sql})
    print(type(rs))
    data = ast.literal_eval(rs)
    print(data)
    # 将问题添加到题库列表
    question_list.append(
        {'id': data[0]['question_id'], 'question': data[0]['question_title'], 'answer': data[0]['answer']}
    )
    answer_list.append(
        {'id': data[0]['question_id'], 'answer': data[0]['answer']}
    )
    # ai回复消息
    ai_msg = f'\n第{current}道题:{data[0]["question_title"]}\n'
    return{
        'messages': [AIMessage(content=ai_msg)],
        'question': question_list,
        'sure_answer': answer_list,
        'total': num,
        'current_index': current,
        'question_id': data[0]['question_id'],
        'exam_step': 'question',
    }