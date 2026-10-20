from pydantic import BaseModel, Field

# 参数校验
class AmapDriverParams(BaseModel):
    start_location: str = Field(..., description='路程的起点')
    end_location: str = Field(..., description='路程的终点')
