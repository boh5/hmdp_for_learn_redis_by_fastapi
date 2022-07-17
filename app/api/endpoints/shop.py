"""
    shop
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import asyncio
import datetime
import threading
from concurrent import futures
from typing import Optional

from fastapi import APIRouter, Path, Query, HTTPException, Body
from sqlmodel import Session, select
from starlette.requests import Request
from fastapi.background import BackgroundTasks

import crud
import models
from app import schemas
from core.config import settings
from db.mysql import engine
from utils.cache import CacheClient
from utils.redis import redis, get_cache_shop_key, lock, get_cache_lock_shop_key, unlock, save_shop_2_redis

router = APIRouter()

cache_client = CacheClient(redis)


# async def query_shop_with_pass_through(id):
#     shop_json_str = await redis.get(get_cache_shop_key(id))
#     if shop_json_str is None:
#         with Session(engine) as sess:
#             statement = select(models.Shop).where(models.Shop.id == id)
#             shop = sess.exec(statement).first()
#         if shop:
#             await redis.setex(get_cache_shop_key(id), settings.CACHE_EXPIRE, shop.json())
#         else:
#             await redis.setex(get_cache_shop_key(id), settings.CACHE_NONE_EXPIRE, '')
#     else:
#         print('query_shop_by_id 没有打到mysql')
#         if not shop_json_str:
#             shop = None
#         else:
#             shop = models.Shop.parse_raw(shop_json_str)
#     return shop


async def query_shop_with_mutex(id):
    shop_json_str = await redis.get(get_cache_shop_key(id))
    if shop_json_str is None:
        try:
            lock_status = await lock(get_cache_lock_shop_key(id))
            if not lock_status:
                await asyncio.sleep(50 / 1000)
                return await query_shop_with_mutex(id)
            with Session(engine) as sess:
                statement = select(models.Shop).where(models.Shop.id == id)
                shop = sess.exec(statement).first()
                print('!!!打到数据库了!!!')
                await asyncio.sleep(200 / 1000)  # 模拟缓存重建延迟
            if shop:
                await redis.setex(get_cache_shop_key(id), settings.CACHE_EXPIRE, shop.json())
            else:
                await redis.setex(get_cache_shop_key(id), settings.CACHE_NONE_EXPIRE, '')
        finally:
            await unlock(get_cache_lock_shop_key(id))
    else:
        print('query_shop_by_id 没有打到mysql')
        if not shop_json_str:
            shop = None
        else:
            shop = models.Shop.parse_raw(shop_json_str)
    return shop


# async def query_shop_with_logical_expire(id, background_tasks: BackgroundTasks):
#     shop_json_str = await redis.get(get_cache_shop_key(id))
#     if shop_json_str is None:
#         return None
#     else:
#         if not shop_json_str:
#             print('query_shop_by_id 没有打到mysql')
#             shop = None
#         else:
#             redis_data = schemas.RedisDataModel[models.Shop].parse_raw(shop_json_str)
#             shop = redis_data.data
#             if datetime.datetime.now() < redis_data.expire_time:
#                 print('query_shop_by_id 没有打到mysql')
#             else:
#                 lock_status = await lock(get_cache_lock_shop_key(id))
#                 if lock_status:
#                     print('当前线程', threading.currentThread().ident)
#
#                     async def rebuild_cache_unlock():
#                         print('当前线程 in', threading.currentThread().ident)
#                         try:
#                             await save_shop_2_redis(id, 20)
#                         finally:
#                             await unlock(get_cache_lock_shop_key(id))
#
#                     print('!!!打到数据库了，独立线程!!!')
#                     background_tasks.add_task(rebuild_cache_unlock)
#
#     return shop


@router.get('/{id}',
            response_model=schemas.GenericResponseModel)
async def query_shop_by_id(
        *,
        id: int = Path,
        background_tasks: BackgroundTasks
):
    # 缓存穿透
    # shop = await cache_client.query_with_pass_through(
    #     key_prefix=settings.CACHE_SHOP_KEY_PREFIX,
    #     pk=id,
    #     model=models.Shop,
    #     db_fallback=crud.shop_crud.get,
    #     expire=settings.CACHE_EXPIRE,
    # )
    # 互斥锁解决缓存击穿，并且解决缓存穿透
    # shop = await query_shop_with_mutex(id)
    # 用逻辑过期解决缓存击穿
    # shop = await query_shop_with_logical_expire(id, background_tasks)
    shop = await cache_client.query_shop_with_logical_expire(
        key_prefix=settings.CACHE_SHOP_KEY_PREFIX,
        pk=id,
        model_class=models.Shop,
        db_fallback=crud.shop_crud.get,
        expire=10,
    )
    if shop:
        return schemas.GenericResponseModel(data=shop)
    else:
        return schemas.GenericResponseModel(success=False, error_msg='店铺不存在')


@router.get('/of/type',
            response_model=schemas.GenericResponseModel)
async def query_shop_by_type(
        *,
        type_id: int = Query(alias='typeId'),
        page: int = Query(alias='current')
):
    if page <= 0:
        page = 1
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.type_id == type_id).limit(settings.MAX_PAGE_SIZE).offset(
            page * settings.MAX_PAGE_SIZE - settings.MAX_PAGE_SIZE)
        results = sess.exec(statement).all()
    data = [r.dict(by_alias=True) for r in results]
    return schemas.GenericResponseModel(data=data)


@router.put('',
            response_model=schemas.GenericResponseModel)
async def update_shop(
        *,
        shop: models.Shop,
):
    if shop.id is None:
        return schemas.GenericResponseModel(success=False, error_msg='店铺id不能为空')
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.id == shop.id)
        shop_in_db = sess.exec(statement).one()
        if not shop_in_db:
            return schemas.GenericResponseModel(success=False, error_msg='该店铺不存在')
        for field, value in shop.dict(exclude={'id', 'create_time', 'update_time'}).items():
            shop_in_db.__setattr__(field, value)
        try:
            sess.add(shop_in_db)
            await redis.delete(get_cache_shop_key(shop.id))
            sess.commit()
        except Exception as e:
            print(e)
            sess.rollback()
    return schemas.GenericResponseModel()
