"""
    voucher
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select


class Voucher(SQLModel, table=True):
    __tablename__ = 'tb_voucher'

    id: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')
    shop_id: int = Field(alias='shopId')
    title: str
    sub_title: Optional[str] = Field(default=None, alias='subTitle')
    rules: Optional[str] = None
    pay_value: int = Field(alias='payValue')
    actual_value: int = Field(alias='actualValue')
    type: int
    status: int
