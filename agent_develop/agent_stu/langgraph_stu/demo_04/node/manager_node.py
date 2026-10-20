from langgraph_stu.demo_04.state.email_state04 import EmailState
from langgraph.types import Command
from langgraph.graph import END
"""
    主管节点，处理任务分发
"""
def manager_node(state: EmailState):
    # 主管决定下一步做什么
    # 获取当前的步骤
    # get可以安全取值，若不存在则返回指定的值
    current_step = state.get('current_step', 'start')
    if current_step == 'start':
        next_node = 'internet'
    elif current_step == 'internet_node':
        next_node = 'query_node'
    elif current_step == 'query_node':
        next_node = 'email_node'
    elif current_step == 'email_node':
        next_node = END
    else:
        next_node = END
    # 使用 command动态跳转
    return Command(goto=next_node)