"""当前登录用户

JWT 里 payload 的结构，CheckTokenUtil 拿它当依赖注入的类型标注用。
（原来这个模块在 DogRAG 的 Chat/entity/ 下，搬过来时没带，导致 common/PermissionUtil 整条链 import 失败）
"""

from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    user_id: int | None = Field(None, description='用户id')
    username: str | None = Field(None, description='用户名')
    role_name: str | None = Field(None, description='角色：admin / user')
