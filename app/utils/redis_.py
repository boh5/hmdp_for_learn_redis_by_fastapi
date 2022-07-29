"""
    redis
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import asyncio
import datetime
import time

# import aioredis
from redis import asyncio as aioredis
from sqlmodel import Session, select

import models
import schemas
import redis
from core.config import settings
from db.mysql import engine

redis_url = f'redis://{settings.REDIS_HOST}'
aio_redis = aioredis.from_url(redis_url, decode_responses=True)
redis = redis.Redis.from_url(redis_url, decode_responses=True)


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
    async with aio_redis.pipeline() as pipe:
        flag, _ = await pipe.setnx(key, '1').expire(key, settings.CACHE_LOCK_EXPIRE).execute()
    if flag:
        return True
    return False


async def unlock(key):
    await aio_redis.delete(key)


async def set_with_logic_expire(key, data, expire):
    model = schemas.RedisDataModel[models.Shop](
        expire_time=datetime.datetime.now() + datetime.timedelta(seconds=expire),
        data=data)
    await aio_redis.set(key, model.json())


async def save_shop_2_redis(id: int, expire: int):
    print('重建缓存. obj: shop, id: {}, expire: {}'.format(id, expire))
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.id == id)
        shop = sess.exec(statement).one()
    await asyncio.sleep(200 / 1000)  # 模拟重建延迟
    await set_with_logic_expire(get_cache_shop_key(id), shop, 20)


# blog like utils
class BlogLikeUtils:
    @staticmethod
    async def is_user_liked_blog(blog_id, user_id):
        score = await aio_redis.zscore(settings.BLOG_LIKED_KEY_PREFIX + str(blog_id), str(user_id))
        if score:
            return True
        return False

    @staticmethod
    async def like_blog_redis(blog_id, user_id):
        await aio_redis.zadd(settings.BLOG_LIKED_KEY_PREFIX + str(blog_id), {str(user_id): time.time_ns()})

    @staticmethod
    async def unlike_blog_redis(blog_id, user_id):
        await aio_redis.zrem(settings.BLOG_LIKED_KEY_PREFIX + str(blog_id), str(user_id))

    @staticmethod
    async def get_top_like_user_ids(blog_id):
        user_ids = await aio_redis.zrange(settings.BLOG_LIKED_KEY_PREFIX + str(blog_id), 0, 4)
        return user_ids


class FollowUtils:
    @staticmethod
    async def add_follow(user_id, follow_user_id):
        await aio_redis.sadd(settings.FOLLOW_KEY_PREFIX + str(user_id), follow_user_id)

    @staticmethod
    async def remove_follow(user_id, follow_user_id):
        await aio_redis.srem(settings.FOLLOW_KEY_PREFIX + str(user_id), follow_user_id)

    @staticmethod
    async def get_common_follow(user_id1, user_id2) -> set:
        commons = await aio_redis.sinter(settings.FOLLOW_KEY_PREFIX + str(user_id1),
                                         settings.FOLLOW_KEY_PREFIX + str(user_id2))
        return commons


class FeedUtils:
    @staticmethod
    async def push_feed(user_id, blog_id):
        await aio_redis.zadd(settings.FEED_KEY_PREFIX + str(user_id), {blog_id: int(time.time() * 1000)})

    @staticmethod
    async def get_feed_blog(user_id, last_id, offset):
        response = await aio_redis.zrevrangebyscore(name=settings.FEED_KEY_PREFIX + str(user_id),
                                                    max=last_id,
                                                    min=0,
                                                    start=offset,
                                                    num=settings.MAX_PAGE_SIZE,
                                                    withscores=True)  # min, max 参数相反是 aioredis 的 bug
        if not response:
            return None, None, None

        blog_ids = []
        min_score = 0
        min_score_count = 0
        for blog_id, score in response:
            blog_ids.append(blog_id)
            if score == min_score:
                min_score_count += 1
            else:
                min_score = score
                min_score_count = 1
        return blog_ids, min_score, min_score_count


class GeoUtils:
    @staticmethod
    async def load_shop_geo_data():
        with Session(engine) as sess:
            shops = sess.exec(
                select(models.Shop)
            ).all()
        shop_type_dict = {}
        for shop in shops:
            if shop.type_id in shop_type_dict:
                shop_type_dict[shop.type_id].append(shop)
            else:
                shop_type_dict[shop.type_id] = [shop]

        for type_id, shop_list in shop_type_dict.items():
            key = settings.SHOP_GEO_KEY_PREFIX + str(type_id)
            values = []
            for shop in shop_list:
                values.extend([shop.x, shop.y, shop.id])
            await aio_redis.geoadd(key, values)

    @staticmethod
    async def search_by_shop_type(shop_type_id, x, y, limit, offset):
        count = offset + limit
        response = await aio_redis.geosearch(
            name=settings.SHOP_GEO_KEY_PREFIX + str(shop_type_id),
            longitude=x,
            latitude=y,
            radius=5000,
            sort='ASC',
            count=count,
            withdist=True,
        )
        return response[offset:]


class SignUtils:

    @staticmethod
    def get_sign_key(now: datetime.datetime, user_id: int):
        return f'{settings.USER_SIGN_KEY_PREFIX}{user_id}:{now.year:04}{now.month:02}'

    @staticmethod
    async def sign(now: datetime.datetime, user_id: int):
        key = SignUtils.get_sign_key(now, user_id)
        await aio_redis.setbit(key, now.day - 1, 1)

    @staticmethod
    async def sign_count(now: datetime.datetime, user_id: int) -> int:
        key = SignUtils.get_sign_key(now, user_id)
        resp = await aio_redis.execute_command('BITFIELD', key, 'GET', 'u' + str(now.day), 0)
        if not resp:
            return 0
        count = 0
        num = resp[0]
        while num:
            if num & 1 == 0:
                break
            else:
                count += 1
                num >>= 1
        return count


if __name__ == '__main__':
    # asyncio.run(save_shop_2_redis(1, 20))
    asyncio.run(GeoUtils.load_shop_geo_data())
  