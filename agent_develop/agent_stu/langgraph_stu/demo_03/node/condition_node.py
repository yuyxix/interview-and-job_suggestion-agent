from langgraph_stu.demo_03.state.email_state03 import EmailState

# 定义query节点条件路由函数
def query_router(state: EmailState):
    # 用 get 兜底：next_step 是可选通道，节点没写过时不该直接崩
    data = state.get('next_step')
    if data == 'email':
        return 'a'
    else:
        return 'b'


# 路由阈值：置信度低于此值就不认为用户真要发邮件，落回 Chat，避免误发
CONFIDENCE_THRESHOLD = 0.8


def router_router(state: EmailState):
    flag = state.get('flag')
    confidence = state.get('confidence') or 0.0
    # 必须同时满足"意图是 SendEmail"和"置信度达标"才真的走发邮件流程
    if flag == 'SendEmail' and confidence >= CONFIDENCE_THRESHOLD:
        # 映射表里 'email' 指向 internet 节点
        return 'email'
    else:
        # 意图不明朗或置信度不足，一律按闲聊处理
        return 'chat'


# 定义query节点的循环路由
def query_for_router(state: EmailState):
    count = state['count']
    next_step = state['next_step']
    if count < 3:
        return 'next'
    else:
        # 判断是否识别出来了
        if next_step == 'email':
            return 'email'
        else:
            return 'end'