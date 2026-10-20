from fastapi import APIRouter
from fastapi.responses import RedirectResponse

default_Page_roter = APIRouter()


@default_Page_roter.get('/')
def default_page():
    # 初始页面就是登录/注册 —— 没登录就不该看到任何业务页面
    return RedirectResponse(url='/static/login.html')