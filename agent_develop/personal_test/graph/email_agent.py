from langgraph.graph import StateGraph, START, END
from node.email_node import email_node
from node.internet_node import internet_node
from node.query_node import query_node
from state.email_state import EmailState
from node.router_node import router_node
from node.chat_node import chat_node
from node.condition_node import query_router, router_router
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
    graph.add_edge("email", END)
    graph.add_edge("chat", END)
    # 编译
    agent = graph.compile()
    return agent
