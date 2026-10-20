from langgraph_stu.demo_03.state.email_state03 import EmailState
from tool.send_email_tool import send_email
from langchain_core.messages import AIMessage


def email_node(state: EmailState):
    # 邮箱
    email = state['email']
    # 标题
    subject = state['subject']
    # 内容
    content = state['content']
    # 调用邮件工具
    rs = send_email.invoke(
        {'to': email, 'subject': subject, 'content': content}
    )
    if rs == '邮件发送成功':
        # 返回结果
        ai_msg = f'\n邮件发送成功\n'
        return {
            'messages': [AIMessage(content=ai_msg)],
            'result': '邮件发送成功'
        }
    if rs != '邮件发送成功':
        ai_msg = f'\n邮件发送失败\n'
        return {
            'messages': [AIMessage(content=ai_msg)],
            'result': '邮件发送失败'
        }

