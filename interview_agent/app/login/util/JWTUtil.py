from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv
load_dotenv()


# 生成token --- payload的内容就是用户信息，用dict封装
def create_token(info: dict) -> str:
    # 拷贝数据
    copy_info = info.copy()
    # 设置token过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    copy_info.update({
        'exp': expire,
        'iat': datetime.now(timezone.utc),
        'user_id': info.get('user_id'),
        'username': info.get('username'),
        'role_name': info.get('role_name')
        })
    # 生成token
    token = jwt.encode(
        claims=copy_info,
        key=os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )
    return token


