from fastapi import HTTPException, status, Header, Depends
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

from app.login.entity.CurrentUserEntity import CurrentUser

load_dotenv()

# 验证token
def verify_token(token: str) -> dict:
    try:
        # 对token进行解密
        payload = jwt.decode(token, key=os.getenv('SECRET_KEY'), algorithms=[os.getenv("ALGORITHM")])
        return payload
    except JWTError:
        print('verify_token17行')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        # print('get_current_user25行')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        # print('get_current_user33行')
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token = parts[1]
    payload = verify_token(token)
    return payload

def current_user(current_user: CurrentUser = Depends(get_current_user)):
    print(current_user)
    return {
        'code': 200,
        'msg': '获取用户信息成功',
        'data': current_user
    }