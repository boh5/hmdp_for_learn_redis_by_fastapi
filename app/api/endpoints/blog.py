"""
    blog
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from typing import Optional

from fastapi import APIRouter, Path, Query
from sqlmodel import Session, select
from starlette.requests import Request

import crud
import models
from app import schemas
from core.config import settings
from db.mysql import engine

router = APIRouter()


@router.post('',
             response_model=schemas.GenericResponseModel)
async def create_blog(
        *,
        request: Request,
        blog_model: schemas.BlogCreateModel,
):
    # user_id = request.session.get('user_id')
    user_id = 1
    blog_model_orm = models.Blog(**blog_model.dict(), user_id=user_id)
    crud.blog_crud.create_blog(blog_model_orm)
    return schemas.GenericResponseModel(data=blog_model_orm.id)


@router.put('/like/{id}',
            response_model=schemas.GenericResponseModel)
async def like_blog(
        *,
        id: int = Path,
):
    crud.blog_crud.like_blog(id)
    return schemas.GenericResponseModel()


@router.get('/of/me',
            response_model=schemas.GenericResponseModel)
async def query_my_blog(
        *,
        request: Request,
        current: Optional[int] = Query(default=1),
):
    # user_id = request.session.get('user_id')
    user_id = 1
    results = crud.blog_crud.list_blog(page=current, user_id=user_id)
    data = [m.dict() for m in results]
    return schemas.GenericResponseModel(data=data)


@router.get('/hot',
            response_model=schemas.GenericResponseModel)
async def query_hot_blog(
        *,
        current: Optional[int] = Query(default=1),
):
    if current <= 0:
        current = 1
    with Session(engine) as sess:
        statement = select(models.Blog).order_by(models.Blog.liked.desc()).limit(settings.MAX_PAGE_SIZE).offset(
            current * settings.MAX_PAGE_SIZE - settings.MAX_PAGE_SIZE)
        blog_results = sess.exec(statement).all()
        data = []
        for blog in blog_results:
            statement = select(models.User).where(models.User.id == blog.user_id)
            user_result = sess.exec(statement).one()
            blog_all = schemas.BlogAllModel(**blog.dict(), name=user_result.nick_name,
                                            icon=user_result.icon)
            data.append(blog_all.dict())
    return schemas.GenericResponseModel(data=data)


@router.get('')
async def read_blog(
        *,
        request: Request,
):
    r = request
    request.session = {'a': 1}
    return 1
