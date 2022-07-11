"""
    user
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = 'tb_user'

    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(nullable=False, max_length=11)
    password: Optional[str] = Field(default=None, nullable=False, max_length=128)
    nick_name: Optional[str] = Field(default=None, max_length=32, alias='nickName')
    icon: Optional[str] = Field(default=None, max_length=255)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='createTime')
