from langgraph_stu.demo_03.state.email_state03 import EmailState
from model.my_model import MyModel
from langchain.messages import AIMessage


def chat_node(state: EmailState):
    model = MyModel.get_local_model()
    rs = model.invoke(input=state['messages'][0].content)
    ai_msg = rs.content
    return {
        'messages': [AIMessage(content=ai_msg)]
    }