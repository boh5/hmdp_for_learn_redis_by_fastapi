"""
    blog
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select


class Blog(SQLModel, table=True):
    __tablename__ = 'tb_blog'

    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(nullable=False, alias='shopId')
    user_id: int = Field(None, nullable=False, alias='userId')
    title: str = Field(max_length=255, nullable=False)
    images: str = Field(max_length=2048, nullable=False)
    content: str = Field(max_length=2048, nullable=False)
    liked: Optional[int] = 0
    comments: Optional[int] = 0
    create_time: datetime.datetime = Field(default=datetime.datetime.now(), alias='createTime')
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.now, alias='updateTime')

    class Config:
        allow_population_by_field_name = True


if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:root@localhost/hmdp')
    with Session(engine) as sess:
        statement = select(Blog)
        statement = 'SELECT * FROM tb_blog'
        results = sess.exec(statement)
        for r in results:
            print(r)
        i = 1
