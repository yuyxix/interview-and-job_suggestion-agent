from langgraph.graph import StateGraph, START, END
from langgraph_stu.demo_02.node.email_node02 import email_node
from langgraph_stu.demo_02.node.internet_node02 import internet_node
from langgraph_stu.demo_02.node.query_node02 import query_node
from langgraph_stu.demo_02.state.email_state02 import EmailState
from langgraph_stu.demo_02.node.condition_node import query_router

"""
    创建一个大脑或者智能体
"""


def email_agent():
    # 获得图形结构
    graph = StateGraph(EmailState)
    # 顺序图添加
    graph.add_node('internet', internet_node)
    graph.add_node('query', query_node)
    graph.add_node('email', email_node)
    # 画边
    graph.add_edge(START, "internet")
    # 新版
    graph.add_edge('internet', 'query')
    # 添加条件边
    # 需要判断的节点+判断函数+判断结果，判断结果可以return一个可映射的标识来指向下一步操作
    graph.add_conditional_edges(
        'query', query_router, {
            "a": 'email',
            'b': END
        }
    )
    graph.add_edge("email", END)
    # 编译
    agent = graph.compile()
    return agent
