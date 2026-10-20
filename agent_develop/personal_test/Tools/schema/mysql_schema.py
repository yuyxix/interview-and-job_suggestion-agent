from pydantic import BaseModel, Field


class MySqlSchema(BaseModel):
    sql: str = Field(description='sql语句')
