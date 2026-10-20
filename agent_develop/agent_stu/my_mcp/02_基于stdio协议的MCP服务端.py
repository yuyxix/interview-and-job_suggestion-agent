import pymysql
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
# 写邮件的库
from email.mime.text import MIMEText
# 发邮件的库
import smtplib
from pydantic import BaseModel, Field

load_dotenv()
# 创建应用程序
app = FastMCP()


# 定义mysql工具
@app.tool('send_email_tool')
def send_email(to: str, subject: str, content: str) -> str:
    """
        发送邮件，发送通知，发送消息
        to: 发送给谁
        subject: 主题
        content: 内容
    """
    try:
        host = os.getenv("SMTP_HOST")
        # 端口选择587就代表要不走 SSL 协议，需要用smtp.starttls()开启邮件发送服务tls
        # 而选择465就代表走 SSL 协议,需要在创建连接对象时使用smtplib.SMTP_SSL()创建对象
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
        msg['To'] = to
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
            smtp.sendmail(sender, to, msg.as_string())
        return '邮箱发送成功'
    except Exception as e:
        print(f'邮件发送异常{e}')
        return '邮件发送异常'

# 定义mysql工具
# 不设置name参数默认为函数名
class MSQSchema(BaseModel):
    sql: str = Field(..., description="sql语句")

@app.tool(
    description='''执行sql语句查询
        数据库模型：
            agent_userinfo 用户信息表,字段：user_id 用户编号，user_name 用户名，email 邮箱, department 部门, num 限制数量
        规则：
            - 禁止生成 DELETE, UPDATE, INSERT, DROP, CREATE, ALTER 语句'''
          )
def mysql_tool(p:MSQSchema) -> str:
    con = None
    cur = None
    try:
        host = os.getenv("MYSQL_HOST")
        port = os.getenv("MYSQL_PORT")
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        db = os.getenv("MYSQL_DB")
        charset = os.getenv("MYSQL_CHARSET")
        if not host or not port or not user or not password or not db or not charset:
            return '数据库连接参数未配置'
        # 兜底操作
        if 'DELETE' in p.sql.upper() or 'UPDATE' in p.sql.upper() or 'INSERT' in p.sql.upper() or 'DROP' in p.sql.upper() or 'CREATE' in p.sql.upper() or 'ALTER' in p.sql.upper():
            return '禁止执行删除、更新、插入、删除、创建、修改数据库结构语句'
        con = pymysql.connect(host=host, port=int(port), user=user, password=password, db=db, charset=charset)
        cur = con.cursor()
        cur.execute(p.sql)
        # 事务提交，针对非查询操作
        # cur.commit()
        rs = cur.fetchall()
        return str(rs)
    except Exception as e:
        return str(e)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


if __name__ == '__main__':
    app.run(transport='stdio')