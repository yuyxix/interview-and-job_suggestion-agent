import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


class GetMysqlCon:
    _host = os.getenv("MYSQL_HOST")
    _port = os.getenv("MYSQL_PORT")
    _user = os.getenv("MYSQL_USER")
    _password = os.getenv("MYSQL_PASSWORD")
    _database = os.getenv("MYSQL_DB")
    _charset = os.getenv("MYSQL_CHARSET")

    @staticmethod
    def get_mysql_con():
        if not GetMysqlCon._host or not GetMysqlCon._port or not GetMysqlCon._user or not GetMysqlCon._password or not GetMysqlCon._database or not GetMysqlCon._charset:
            return '数据库连接参数未配置'
        return pymysql.connect(
            host=GetMysqlCon._host,
            port=int(GetMysqlCon._port),
            user=GetMysqlCon._user,
            password=GetMysqlCon._password,
            database=GetMysqlCon._database,
            charset=GetMysqlCon._charset,
            cursorclass=pymysql.cursors.DictCursor
        )

    @staticmethod
    def close_mysql_con(cursor, con):
        cursor.close()
        con.close()

