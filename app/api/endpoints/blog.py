"""
    blog
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import functools
from typing import Optional

from fastapi import APIRouter, Path, Query, Depends
from sqlmodel import Session, select, col
from starlette.requests import Request

import crud
import models
from api import deps
from app import schemas
from core.config import settings
from db.mysql import engine
from utils.redis_ import BlogLikeUtils, FollowUtils, FeedUtils

router = APIRouter()


@router.post('',
             response_model=schemas.GenericResponseModel)
async def create_blog(
        *,
        blog_model: models.Blog,
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    blog_model.user_id = user.id
    try:
        blog_model = crud.blog_crud.create_blog(blog_model)
    except Exception as e:
        print(e)
        return schemas.GenericResponseModel(success=False, error_msg='新增笔记失败')
    else:
        follower_ids = crud.follow_crud.get_fan_ids(user.id)
        for follower_id in follower_ids:
            await FeedUtils.push_feed(follower_id, blog_model.id)
    return schemas.GenericResponseModel(data=blog_model.id)


@router.put('/like/{blog_id}',
            response_model=schemas.GenericResponseModel)
async def like_blog(
        *,
        blog_id: int = Path,
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    is_liked = await BlogLikeUtils.is_user_liked_blog(blog_id, user.id)
    if not is_liked:
        await BlogLikeUtils.like_blog_redis(blog_id, user.id)
        crud.blog_crud.like_blog(blog_id)
    else:
        await BlogLikeUtils.unlike_blog_redis(blog_id, user.id)
        crud.blog_crud.unlike_blog(blog_id)

    return schemas.GenericResponseModel()


@router.get('/of/me',
            response_model=schemas.GenericResponseModel)
async def query_my_blog(
        *,
        current: Optional[int] = Query(default=1),
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    user_id = user.id
    blogs = crud.blog_crud.list_blog(page=current, user_id=user_id)
    return schemas.GenericResponseModel(data=blogs)


@router.get('/of/user',
            response_model=schemas.GenericResponseModel)
async def get_blog_of_user(
        *,
        user_id: int = Query(alias='id'),
        page: Optional[int] = Query(default=1, alias='current'),
):
    blogs = crud.blog_crud.list_blog(page=page, user_id=user_id)
    return schemas.GenericResponseModel(data=blogs)


@router.get('/of/follow',
            response_model=schemas.GenericResponseModel[schemas.GenericScrollResponseModel[schemas.BlogAllModel]])
async def get_blog_of_follow(
        *,
        last_id: int = Query(alias='lastId'),
        offset: int = Query(0),
        user: schemas.UserBaseModel = Depends(deps.verify_user),
):
    blog_ids, min_time, offset = await FeedUtils.get_feed_blog(user.id, last_id, offset)
    if not blog_ids:
        return schemas.GenericResponseModel()
    blogs = crud.blog_crud.list_id_in(blog_ids)
    blogs.sort(key=functools.cmp_to_key(lambda x, y: blog_ids.index(str(x.id)) - blog_ids.index(str(y.id))))
    data = []
    for blog in blogs:
        blog_all = await get_blog_all(blog, user)
        data.append(blog_all)

    return schemas.GenericResponseModel(
        data=schemas.GenericScrollResponseModel(list_=data, min_time=min_time, offset=offset))


@router.get('/hot',
            response_model=schemas.GenericResponseModel)
async def query_hot_blog(
        *,
        current: Optional[int] = Query(default=1),
        user: schemas.UserBaseModel = Depends(deps.try_user),
):
    if current <= 0:
        current = 1
    with Session(engine) as sess:
        statement = select(models.Blog).order_by(models.Blog.liked.desc()).limit(settings.MAX_PAGE_SIZE).offset(
            current * settings.MAX_PAGE_SIZE - settings.MAX_PAGE_SIZE)
        blog_results = sess.exec(statement).all()
        data = []
        for blog in blog_results:
            blog_all = await get_blog_all(blog, user)
            data.append(blog_all)
    return schemas.GenericResponseModel(data=data)


@router.get('/{blog_id}',
            response_model=schemas.GenericResponseModel)
async def read_blog(
        *,
        blog_id: int = Path(),
        user: schemas.UserBaseModel = Depends(deps.try_user)
):
    with Session(engine) as sess:
        statement = select(models.Blog).where(models.Blog.id == blog_id)
        blog = sess.exec(statement).first()
        if not blog:
            return schemas.GenericResponseModel(success=False, error_msg='笔记不存在')
    blog_all = await get_blog_all(blog, user)
    return schemas.GenericResponseModel(data=blog_all)


@router.get('/likes/{blog_id}',
            response_model=schemas.GenericResponseModel)
async def blog_likes(
        *,
        blog_id: int = Path()
):
    user_ids = await BlogLikeUtils.get_top_like_user_ids(blog_id)
    if not user_ids:
        return schemas.GenericResponseModel()
    with Session(engine) as sess:
        users = sess.exec(select(models.User).where(col(models.User.id).in_(user_ids))).all()
    users.sort(key=functools.cmp_to_key(lambda x, y: user_ids.index(str(x.id)) - user_ids.index(str(y.id))))
    return schemas.GenericResponseModel(data=users)


async def get_blog_all(blog: models.Blog, cur_user: Optional[schemas.UserBaseModel]) -> schemas.BlogAllModel:
    with Session(engine) as sess:
        statement = select(models.User).where(models.User.id == blog.user_id)
        user = sess.exec(statement).first()
    if cur_user:
        is_liked = await BlogLikeUtils.is_user_liked_blog(blog.id, cur_user.id)
    else:
        is_liked = False
    blog_all = schemas.BlogAllModel(**blog.dict(), is_like=is_liked, name=user.nick_name, icon=user.icon)
    return blog_all
