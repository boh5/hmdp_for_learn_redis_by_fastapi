"""
    redis
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import asyncio
import datetime

import aioredis
from sqlmodel import Session, select

import models
import schemas
from core.config import settings
from db.mysql import engine

redis = aioredis.from_url(f'redis://{settings.REDIS_HOST}', decode_responses=True)


def get_login_code_key(phone: str) -> str:
    return settings.LOGIN_CODE_KEY_PREFIX + phone


def get_login_user_obj_key(token: str) -> str:
    return settings.LOGIN_USER_OBJ_KEY_PREFIX + token


def get_cache_shop_key(shop_id: int) -> str:
    return settings.CACHE_SHOP_KEY_PREFIX + str(shop_id)


def get_cache_shop_type_list_key() -> str:
    return settings.CACHE_SHOP_TYPE_KEY_PREFIX + 'list'


def get_cache_lock_shop_key(id: int) -> str:
    return settings.CACHE_LOCK_KEY_PREFIX + 'shop:' + str(id)


async def lock(key):
    async with redis.pipeline() as pipe:
        flag, _ = await pipe.setnx(key, '1').expire(key, settings.CACHE_LOCK_EXPIRE).execute()
    if flag:
        return True
    return False


async def unlock(key):
    await redis.delete(key)


async def set_with_logic_expire(key, data, expire):
    model = schemas.RedisDataModel[models.Shop](
        expire_time=datetime.datetime.now() + datetime.timedelta(seconds=expire),
        data=data)
    await redis.set(key, model.json())


async def save_shop_2_redis(id: int, expire: int):
    print('重建缓存. obj: shop, id: {}, expire: {}'.format(id, expire))
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.id == id)
        shop = sess.exec(statement).one()
    await asyncio.sleep(200 / 1000)  # 模拟重建延迟
    await set_with_logic_expire(get_cache_shop_key(id), shop, 20)


if __name__ == '__main__':
    asyncio.run(save_shop_2_redis(1, 20))
