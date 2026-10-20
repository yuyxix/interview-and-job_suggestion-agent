from langchain_core.messages import HumanMessage
from app.ai.agent.multi_agent.node.router_agent import router_agent
from app.ai.agent.multi_agent.state.exam_state import ExamState
from langgraph.types import Command
from langgraph.graph import END
from app.ai.agent.multi_agent.memory.manage.memory_manager import MemoryManager, get_collection
"""
    主管节点，中枢，负责调用其他节点
"""

# 定义记忆关键字匹配（为大模型判断兜底，同时增加响应速度）
memory_keyword = [
    '上一个问题', '上一题', '刚才的问题', '刚才我说',
    '上一句', '我刚才说了什么', '我刚才说了啥', '我刚刚说了什么',
    "程序员是不是都容易秃头啊",
    "面试官一般长什么样会不会很凶", "你觉得AI会取代Java开发吗", "35岁危机是真的吗好焦虑",
    "产品经理和项目经理哪个更累", "听说大厂都在裁员真的假的", "学Python是不是比学Java简单",
    "你们AI也会加班吗", "今天上班被领导骂了心情好差", "周末想放松一下有什么推荐的电影或游戏吗",
    "最近失眠严重怎么办", "我和同事闹矛盾了该怎么相处", "明天要早起通勤好痛苦啊",
    "端午节去哪玩比较好", "帮我写个朋友圈文案吐槽一下加班", "你好", "在吗",
    "嗨", "谢谢", "辛苦了",
    "拜拜", "你叫什么名字是谁开发的", "你能做什么介绍一下你自己",
    "刚才那个问题我没看懂再说一遍", "今天天气怎么样", "讲个笑话", "给我唱首歌", "1+1等于几"
]


# 定义函数，判断问题是否在记忆中
def is_keyword(question):
    for keyword in memory_keyword:
        if keyword in question:
            return True
    return False


def manager_node(state: ExamState):
    # 获取当前出题状态
    continue_question = state.get('continue_question', True)
    # 获取考试状态
    exam_state = state.get('exam_step', 'start')
    print(f'当前考试状态:{exam_state}')
    print(f'状态:{state}')
    # 获取用户输入问题
    last_msg = state['messages'][-1]
    if isinstance(last_msg, HumanMessage):
        user_input = last_msg.content

        # 考试进行中（已经出完题、正在等用户回答）
        # 这时用户输入默认就是"答案"，不再跑路由模型。
        # 原因：router 里的 answer 指的是"让 AI 讲解/给出答案"，
        # 和"用户正在作答"不是一回事 —— 正常作答会被误判成 chat，
        # 然后被"先把题答完"拦下来（就是这个 bug）。
        # 另外这里也不能转 chat：chat_node 会把 exam_step 改成 'chat'，
        # 当前题目（question / question_id / current_index）的状态就丢了。
        if exam_state == 'question' and user_input.strip():
            return Command(goto='answer')

        if is_keyword(user_input):
            print('关键字命中，关键字匹配')
            # 进入到聊天+记忆节点
            return Command(goto='chat')
        print('意图识别模型兜底')
        route = router_agent(user_input)
        print(f'路由结果{route}')
        if route == 'exam':
            return Command(goto='intention')
        elif route == 'chat':
            return Command(goto='chat')
        elif route == 'answer':
            return Command(goto='answer')
        elif route == 'job':
            return Command(goto='get_job')
    else:
        user_input = ''
    print(f'用户输入:{user_input}')
    # 如果是第一次进入
    if exam_state == 'start':
        return Command(goto='intention')
    elif exam_state == 'intention':
        return Command(goto='question')
    elif exam_state == 'question':
        if user_input == '':
            print('等待用户输入答案')
            return Command(goto=END)
        else:
            return Command(goto='answer')
    elif exam_state == 'answer':
        if continue_question:
            print('继续出题')
            return Command(goto='question')
        else:
            print('答题结束')
            return Command(goto='evaluate')
    elif exam_state == 'evaluate':
        return Command(goto='evaluate')
    elif exam_state == 'end':
        return Command(goto=END, update={
            'exam_step': 'start',
            'question': [],
            'current_index': 0,
            'user_answer': [],
            'sure_answer': [],
        })
    else:
        return Command(goto=END)
