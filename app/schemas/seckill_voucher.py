"""
    seckill_voucher
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/25
"""
import datetime
from typing import Optional

from pydantic import Field, BaseModel


class SeckillVoucherCreateModel(BaseModel):
    shop_id: int = Field(alias='shopId')
    title: str
    sub_title: Optional[str] = Field(default=None, alias='subTitle')
    rules: Optional[str] = None
    pay_value: int = Field(alias='payValue')
    actual_value: int = Field(alias='actualValue')
    type: int
    status: int

    stock: Optional[int] = None
    begin_time: Optional[datetime.datetime] = Field(None, alias='beginTime')
    end_time: Optional[datetime.datetime] = Field(None, alias='endTime')

    class Config:
        allow_population_by_field_name = True


class SeckillVoucherModel(SeckillVoucherCreateModel):
    id: Optional[int] = Field(default=None)
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')

    class Config:
        allow_population_by_field_name = True
