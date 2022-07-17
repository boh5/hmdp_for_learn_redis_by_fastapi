"""
    redis
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/17
"""
import datetime
from typing import TypeVar, Generic

from pydantic.generics import GenericModel

DataT = TypeVar('DataT')


class RedisDataModel(GenericModel, Generic[DataT]):
    expire_time: datetime.datetime
    data: DataT
