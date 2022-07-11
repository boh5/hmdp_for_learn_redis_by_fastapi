"""
    user
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
from typing import Optional

from pydantic import BaseModel, Field, root_validator


class UserBaseModel(BaseModel):
    id: int
    nick_name: Optional[str] = Field(default=None, alias='nickName')
    icon: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class UserLoginModel(BaseModel):
    phone: str
    code: Optional[str] = None
    password: Optional[str] = None

    @root_validator
    def check_code_password_both_none(cls, values):
        code, password = values.get('code'), values.get('password')
        if code is None and password is None:
            raise ValueError('code and password can not be all None')
        return values
