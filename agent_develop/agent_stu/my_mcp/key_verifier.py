"""
    可以为mcp服务添加密钥验证
    原理：
        - 创建一个新的验证器类，继承自 `TokenVerifier`。
        必须实现 `verify_token` 方法，即根据自己的业务需求改写这个方法
    本案例做简单的演示
"""

from fastmcp.server.auth import TokenVerifier, AccessToken


class KeyVerifier(TokenVerifier):
    # 改写类中的verify_token方法
    async def verify_token(self, token: str) -> AccessToken | None:
        if token == '123456':
            return AccessToken(
                token=token,
                client_id='123456',
                scopes=['read', 'write']  # 允许访问的权限信息
            )
        else:
            return None