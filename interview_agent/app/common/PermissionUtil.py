# 验证用户是否有访问该接口的权限
from fastapi import Header, HTTPException, status

from app.common.CheckTokenUtil import verify_token


# 工厂函数，接受一个列表，列表中是允许访问的role_name
def has_roles(*allowed_roles: str):
    # 获取请求头的Authorization中的内容
    # Authorization中的内容：Bearer + token
    def user_permission(authorization: str = Header(None)):
        # print(authorization)
        if not authorization:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        token = parts[1]

        payload = verify_token(token)
        role_name = payload['role_name']
        if role_name not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="没有权限")
        return payload
    return user_permission
