from langchain.tools import tool
from Tools.schema.send_email_schema import EmailParams
from dotenv import load_dotenv
import os
# 写邮件的库
from email.mime.text import MIMEText
# 发邮件的库
import smtplib

load_dotenv()


# 定义工具
@tool(
    # 工具名字
    name_or_callable='send_email',
    # 设置参数校验
    args_schema=EmailParams
)
def send_email(email: str, subject: str, content: str) -> str:
    """
    给指定姓名的人发送指定内容的邮箱
    """
    try:
        host = os.getenv("SMTP_HOST")
        port = os.getenv("SMTP_PORT")
        password = os.getenv("SENDER_EMAIL_PASSWORD")
        sender = os.getenv("SENDER_EMAIL")
        # 判断读取是否成功
        if not sender or not password or not host or not port:
            return '邮件配置读取失败'
        # 创建邮件对象
        msg = MIMEText(content)
        # 定义发件人
        msg['From'] = sender
        # 定义收件人
        msg['To'] = email
        # 定义主题
        msg['Subject'] = subject
        # 创建一个连接服务器邮箱的地址
        """
            相较于直接创建对象的方式创建连接对象，
            这样创建的好处是无论出现异常，或是其他问题，或是没有问题，链接都会自动退出
            直接创建则需要smtp.quit手动退出
        """
        with smtplib.SMTP_SSL(host, int(port)) as smtp:
            # 登录邮件服务器
            smtp.login(sender, password)
            # 发邮件
            smtp.sendmail(sender, email, msg.as_string())
        return '邮件发送成功'
    except Exception as e:
        print(f'邮件发送异常{e}')
        return '邮件发送异常'

if __name__ == '__main__':
    send_email.invoke({'email': '3547135815@qq.com', 'subject': '测试', 'content': '这是测试邮件'})
