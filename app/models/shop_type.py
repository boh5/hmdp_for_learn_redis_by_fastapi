"""
    shop_type
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ShopType(SQLModel, table=True):
    __tablename__ = 'tb_shop_type'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, max_length=32)
    icon: Optional[str] = Field(default=None, max_length=255)
    sort: Optional[int] = Field(default=None)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='createTime')
