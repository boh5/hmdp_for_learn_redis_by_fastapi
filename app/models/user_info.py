"""
    user_info
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/28
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserInfo(SQLModel, table=True):
    __tablename__ = 'tb_user_info'

    user_id: Optional[int] = Field(default=None, primary_key=True, alias='userId')
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')

    city: Optional[str] = Field('')
    introduce: Optional[str] = Field('')
    fans: Optional[int] = Field(0)
    followee: Optional[int] = Field(0)
    gender: Optional[int] = Field(0)
    birthday: Optional[datetime.date] = Field(None)
    credits: Optional[int] = Field(0)
    level: Optional[int] = Field(0)

    class Config:
        allow_population_by_field_name = True
