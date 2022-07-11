"""
    blog
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from typing import List

import pymysql.cursors
from sqlmodel import Session, select

import models
from app import schemas
from app.core.config import settings
from app.crud.base import BaseCRUD
from db.mysql import engine


class BlogCRUD:
    def create_blog(self, blog_model: models.Blog) -> None:
        with Session(engine) as sess:
            sess.add(blog_model)
            sess.commit()
            sess.refresh(blog_model)

    def like_blog(self, blog_id):
        with Session(engine) as sess:
            statement = select(models.Blog).where(models.Blog.id == blog_id)
            results = sess.exec(statement)
            blog = results.one()
            blog.liked += 1
            sess.add(blog)
            sess.commit()

    def list_blog(self, page: int = 1, page_size: int = 10, user_id: int = None, ) -> List[models.Blog]:
        if page <= 0:
            page = 1
        with Session(engine) as sess:
            statement = select(models.Blog).limit(page_size).offset(page * page_size - page_size)
            if user_id:
                statement = statement.where(models.Blog.user_id == user_id)
            results = sess.exec(statement).all()
        return results


blog_crud = BlogCRUD()
