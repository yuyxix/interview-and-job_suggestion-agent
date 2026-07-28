# # pymysql库 ---操作数据库的库
# import pymysql
#
# # 创建连接对象
# conn = pymysql.connect(
#     # 连接数据库服务所在的ip地址
#     host='localhost',
#     # 数据库服务器运行的端口号
#     port=3306,
#     # 数据库的用户名
#     user='root',
#     # 数据库的密码
#     password='3278708004cyx',
#     # 数据库的名称
#     database='login',
#     # 连接的字符编码
#     charset='utf8'
# )
#
# # 通过账号查询数据库数据
# # 2.通过链接对象获取游标对象 --- 操作数据库的对象
# cur = conn.cursor()
#
# # 3.写操作数据库的命令 --- 通过账号查询数据库数据
# sql = 'select * from user'  # %变量占位符，有顺序问题
#
# # 4.执行SQL语句，若SQL语句中有参数，就要赋值【值放在列表里面】
# # username = input('请输入用户名')
# ex = cur.execute(sql)
#
# # 5.查询操作不会对数据库中的数据产生影响，不需要做事务处理
# # 查询操作得到的是数据内容，需要通过fetchall方法获取---返回值元组，每一个数据就是元组中的元组
# # 元组的数据内容值只有对应的值，没有列名 --- 按照表的结构顺序展示的
# data = cur.fetchall()
# print(data)
#
#
# # 没数据会返回一个空元组


