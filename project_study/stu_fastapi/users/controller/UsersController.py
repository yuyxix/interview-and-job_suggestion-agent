# 接口定义的文件
from users.entity.Users import Users
from users.service import UserService
from fastapi import APIRouter

# 子路由对象
api_router = APIRouter()

# 登录
@api_router.post("/login")
def login(users: Users):
    return UserService.login(users)