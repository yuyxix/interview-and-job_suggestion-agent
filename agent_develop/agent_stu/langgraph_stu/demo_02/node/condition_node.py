from langgraph_stu.demo_02.state.email_state02 import EmailState


# 定义query节点条件路由函数
def query_router(state: EmailState):
    data = state['next_step']
    if data == 'email':
        return 'a'
    else:
        return 'b'