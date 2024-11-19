from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional
from datetime import date


class initArgs(BaseModel):
    engine: str = Field(..., min_length=3, max_length=50, example="postgres")
    database: str = Field(..., min_length=3, max_length=50, example="demo")
    hostname: str = Field(..., min_length=3, max_length=50, example="localhost")
    port: str = Field(..., min_length=3, max_length=50, example="5432")
    username: str = Field(..., min_length=3, max_length=50, example="user")
    password: str = Field(..., min_length=3, max_length=50,
                          example="strongpassword")

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True
        orm_mode = True
