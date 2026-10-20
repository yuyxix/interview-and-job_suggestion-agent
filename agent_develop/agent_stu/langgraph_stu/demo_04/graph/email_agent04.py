from langgraph.graph import StateGraph, START
from langgraph_stu.demo_04.node.email_node04 import email_node
from langgraph_stu.demo_04.node.internet_node04 import internet_node
from langgraph_stu.demo_04.node.query_node04 import query_node
from langgraph_stu.demo_04.state.email_state04 import EmailState
from langgraph_stu.demo_04.node.manager_node import manager_node


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
    graph.add_node('manager_node', manager_node)
    # 画边
    graph.add_edge(START, "manager_node")
    graph.add_edge("internet", 'manager_node')
    graph.add_edge("query", "manager_node")
    graph.add_edge("email", "manager_node")
    # 编译
    # 通过这种方式在langgraph种添加人工审核机制，这里意思就是在'email'之前人工审核
    agent = graph.compile()
    return agent
