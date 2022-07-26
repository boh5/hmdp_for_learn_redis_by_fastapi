"""
    seckill_voucher
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/25
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class SeckillVoucher(SQLModel, table=True):
    __tablename__ = 'tb_seckill_voucher'

    voucher_id: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')
    stock: int
    begin_time: datetime.datetime = Field(alias='beginTime')
    end_time: datetime.datetime = Field(alias='endTime')

    class Config:
        allow_population_by_field_name = True
