"""
    voucher_order
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/25
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class VoucherOrder(SQLModel, table=True):
    __tablename__ = 'tb_voucher_order'

    id: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')

    user_id: int = Field(alias='userId')
    voucher_id: int = Field(alias='voucherId')
    pay_type: int = Field(1, alias='payType')
    status: int = 1
    pay_time: Optional[datetime.datetime] = Field(None, alias='payTime')
    use_time: Optional[datetime.datetime] = Field(None, alias='useTime')
    refund_time: Optional[datetime.datetime] = Field(None, alias='refundTime')

    class Config:
        allow_population_by_field_name = True
