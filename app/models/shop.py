"""
    shop
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select


class Shop(SQLModel, table=True):
    __tablename__ = 'tb_shop'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type_id: int = Field(alias='typeId')
    images: str
    area: Optional[str] = None
    address: str
    x: float
    x: float
    avg_price: Optional[int] = Field(default=None, alias='avgPrice')
    sold: int
    comments: int
    score: int
    open_hours: Optional[str]
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')
