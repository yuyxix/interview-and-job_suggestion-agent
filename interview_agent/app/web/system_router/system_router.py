"""系统路由：登录 / 注册 / 管理

把三个控制器里的 router 汇总成一个，main.py 只要 include 这一个就行。

挂载后的路径：
    登录    GET  /login?email=&password=
    注册    GET  /sendemail?email=          发验证码
            POST /VerifyCode                校验验证码（顺便在 register_info 里占位）
            POST /register                  提交注册
    管理    GET  /admin/users               需要 admin 角色
            GET  /admin/profiles            只读查看所有用户画像
            GET  /admin/profile/{user_id}   只读查看单个用户画像
            GET  /admin/get_user
            POST /admin/delete_user/{username}
            PUT  /admin/change_role
"""

from fastapi import APIRouter

from app.web.system_router.AdminController import admin_router
from app.web.system_router.LoginController import login_router
from app.web.system_router.RegisterController import register_router

system_router = APIRouter()

system_router.include_router(login_router)
system_router.include_router(register_router)
# 管理接口加个 /admin 前缀，跟业务路由区分开
system_router.include_router(admin_router, prefix='/admin')
