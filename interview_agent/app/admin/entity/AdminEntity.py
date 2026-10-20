from pydantic import BaseModel, Field

class ChangeRolesEntity(BaseModel):
    username: str = Field(..., description='用户名')
    role_name: str = Field(..., description='角色名')
