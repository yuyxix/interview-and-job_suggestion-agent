from fastapi import APIRouter

from app.login.service import LoginService

login_router = APIRouter()

# 登录界面
@login_router.get(
    path='/login',
    summary='登录',
    description='通过验证账号密码实现登录',
)
def login(email: str, password: str):
    return LoginService.check_account(email, password)
