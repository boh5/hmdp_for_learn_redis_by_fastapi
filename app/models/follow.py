"""
    follow
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/28
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select


class Follow(SQLModel, table=True):
    __tablename__ = 'tb_follow'

    id: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')

    user_id: int = Field(default=None, nullable=False, alias='userId')
    follow_user_id: int = Field(nullable=False, alias='followUserId')

    class Config:
        allow_population_by_field_name = True
