from langgraph.graph import StateGraph, START, END
from langgraph_stu.demo_01.node.email_node01 import email_node
from langgraph_stu.demo_01.node.internet_node01 import internet_node
from langgraph_stu.demo_01.node.query_node01 import query_node
from langgraph_stu.demo_01.state.email_state01 import EmailState


"""
    创建一个大脑或者智能体
"""


def email_agent(m):
    # 获得图形结构
    graph = StateGraph(EmailState)
    # 顺序图添加
    graph.add_node('internet', internet_node)
    graph.add_node('query', query_node)
    graph.add_node('email', email_node)
    # 画边
    # 老版本设置起点
    # graph.set_entry_point("internet")
    graph.add_edge(START, "internet")
    # 新版
    graph.add_edge('internet', 'query')
    graph.add_edge("query", "email")
    graph.add_edge("email", END)
    # 编译
    # 增加审核机制
    agent = graph.compile(
        interrupt_before=['email'],
        checkpointer=m,     # 人工审核必须添加检查点
    )
    return agent
