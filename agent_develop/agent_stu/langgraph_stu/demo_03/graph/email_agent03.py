from langgraph.graph import StateGraph, START, END

from langgraph_stu.demo_03.node.chat_node import chat_node
from langgraph_stu.demo_03.node.email_node03 import email_node
from langgraph_stu.demo_03.node.internet_node03 import internet_node
from langgraph_stu.demo_03.node.query_node03 import query_node
from langgraph_stu.demo_03.node.router_node import router_node
from langgraph_stu.demo_03.state.email_state03 import EmailState
from langgraph_stu.demo_03.node.condition_node import query_router, router_router, query_for_router

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
    graph.add_node('chat', chat_node)
    graph.add_node('router', router_node)

    # 画边
    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", router_router, {
        'email': 'internet',
        'chat': 'chat'
    })
    graph.add_edge("internet", "query")
    graph.add_conditional_edges(
        'query', query_router, {
            "a": 'email',
            'b': END
        }
    )
    # 添加循环边
    graph.add_conditional_edges(
        'query', query_for_router, {
            'next': 'internet',
            'end': END
        }
    )
    graph.add_edge("email", END)
    graph.add_edge("chat", END)
    # 编译
    agent = graph.compile()
    return agent
