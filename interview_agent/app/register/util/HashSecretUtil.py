# 密码加密工具
from passlib.context import CryptContext

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(origin_password):
    return crypt_context.hash(origin_password)


def verify_password(origin_password, hashed_password):
    return crypt_context.verify(origin_password, hashed_password)