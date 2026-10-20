from state.email_state import EmailState
from Tools.mysql_tool import mysql_tool
from langchain_core.messages import ToolMessage
import ast
"""
    查询节点
"""


def query_node(state: EmailState):
    # 获取用户姓名
    name = state['name']
    # 调用工具
    rs = mysql_tool.invoke({
        'sql': f"select email from agent_userinfo where user_name = '{name}'"
    })
    # 游标是 DictCursor，fetchall() 返回 list[dict]，空结果是 '[]' 而不是 '()'
    if rs == '[]':
        return {
            'messages': [ToolMessage(content=f"用户邮箱不存在", tool_call_id='query_node')],
            'result': '用户邮箱不存在',
            'next_step': 'end'
        }
    # 获取邮箱
    # 获取到的邮箱是一个字典放在字符串里
    email = ast.literal_eval(rs)
    # 定义结果
    tool_msg = f"\n查询节点成功\n邮箱是：{email[0]['email']}"
    return{
        'messages': [ToolMessage(content=tool_msg, tool_call_id='query_node')],
        'result': '\n查询节点成功\n',
        'email': email[0]['email'],
        'next_step': 'email'
    }