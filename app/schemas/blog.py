"""
    blog
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import datetime
from typing import Optional

from pydantic import BaseModel, Field

import models


class BlogModel(BaseModel):
    id: int
    shop_id: int = Field(alias='shopId')
    user_id: int = Field(alias='userId')
    title: str
    images: str
    content: str
    liked: int
    comments: int


class BlogCreateModel(BaseModel):
    shop_id: int = Field(alias='shopId')
    title: str
    images: str
    content: str
    liked: Optional[int] = None
    comments: Optional[int] = None


class BlogAllModel(BlogModel):
    icon: Optional[str]
    name: Optional[str]
    is_like: Optional[bool] = Field(default=True, alias='isLike')
    create_time: datetime.datetime = Field(alias='createTime')
    update_time: datetime.datetime = Field(alias='updateTime')

    class Config:
        allow_population_by_field_name= True


class BlogResponseModel(BlogModel):
    create_time: datetime.datetime = Field(alias='createTime')
    update_time: datetime.datetime = Field(alias='updateTime')
