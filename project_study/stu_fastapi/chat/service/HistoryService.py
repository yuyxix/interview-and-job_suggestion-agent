from chat.dao import HistoryDao

def query_history_menu(username):
    # 获取结果
    result = HistoryDao.query_history_menu(username)
    # 包装结果
    data_list = []
    for item in result:
        data_list.append({
            'historyId': item['historyId'],
            'title': item['question'],
            'time': item['createTime'].strftime('%Y-%m-%d %H:%M:%S'),
        })
    return {
        'code': 200,
        'msg': '查询成功',
        'data': data_list
    }

# 查询某一条详细的对话记录
def conversation_log(historyId):
    result = HistoryDao.conversation_log(historyId)
    data_list = []
    for item in result:
        data_list.append({
            'role': 'user',
            'content': item['question'],
        })
        data_list.append({
            'role': 'assistant',
            'content': item['answer'],
        })
    return {
        'code': 200,
        'msg': '查询成功',
        'data': data_list
    }

if __name__ == '__main__':
    print(conversation_log(1))