"""
    cache
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/17
"""
import asyncio
import concurrent.futures
import datetime
import threading
from typing import Callable, Hashable, Any, Sequence, Type, Optional

from aioredis import Redis
from pydantic import BaseModel
from sqlmodel import Session, select

import models
import schemas
from core.config import settings
from db.mysql import engine
from utils.redis_ import lock, get_cache_lock_shop_key, set_with_logic_expire, unlock, aio_redis


class CacheClient:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, model: BaseModel, expire: int):
        await self.redis.setex(key, expire, model.json())

    async def set_with_logical_expire(self, key: str, model: BaseModel, expire: int):
        redis_data = schemas.RedisDataModel[type(model)](
            expire_time=datetime.datetime.now() + datetime.timedelta(seconds=expire),
            data=model,
        )
        await self.redis.set(key, redis_data.json())

    async def query_with_pass_through(self,
                                      key_prefix: str,
                                      pk: int,
                                      model_class: Type[BaseModel],
                                      db_fallback: Callable[[Hashable], BaseModel],
                                      expire: int,
                                      ) -> Optional[BaseModel]:
        key = key_prefix + str(pk)
        json_str = await self.redis.get(key)
        if json_str is None:
            model = db_fallback(pk)
            if model:
                await self.set(key, model, expire)
            else:
                await self.redis.setex(key, expire, '')
        else:
            print('query_shop_by_id 没有打到mysql')
            if not json_str:
                model = None
            else:
                model = model_class.parse_raw(json_str)
        return model

    async def query_shop_with_logical_expire(self,
                                             key_prefix: str,
                                             pk: int,
                                             model_class: Type[BaseModel],
                                             db_fallback: Callable[[Hashable], BaseModel],
                                             expire: int,
                                             ) -> Optional[BaseModel]:
        key = key_prefix + str(pk)
        json_str = await self.redis.get(key)
        if json_str is None:
            model = None
        else:
            if not json_str:
                print('query_shop_by_id 没有打到mysql')
                model = None
            else:
                redis_data = schemas.RedisDataModel[model_class].parse_raw(json_str)
                model = redis_data.data
                if datetime.datetime.now() < redis_data.expire_time:
                    print('query_shop_by_id 没有打到mysql')
                else:
                    lock_status = await lock(get_cache_lock_shop_key(pk))
                    print('outer thead id', threading.currentThread().ident)
                    if lock_status:
                        async def rebuild_cache_unlock():
                            print('inner thead id', threading.currentThread().ident)
                            try:
                                db_model = db_fallback(pk)
                                await asyncio.sleep(10)
                                await self.set_with_logical_expire(key, db_model, expire)
                            finally:
                                await unlock(get_cache_lock_shop_key(pk))

                        print('!!!打到数据库了，独立线程!!!')
                        asyncio.create_task(rebuild_cache_unlock())
                    else:
                        print('query_shop_by_id 没用获取到锁 没有打到mysql')

        return model


if __name__ == '__main__':
    cache_client = CacheClient(redis=aio_redis)


    async def save_shop_to_redis(shop: models.Shop):
        key = settings.CACHE_SHOP_KEY_PREFIX + str(shop.id)
        await cache_client.set_with_logical_expire(key, shop, 10)


    async def main():

        with Session(engine) as sess:
            shops = sess.exec(select(models.Shop)).all()
        tasks = []
        for shop in shops:
            tasks.append(asyncio.create_task(save_shop_to_redis(shop)))
        done, _ = await asyncio.wait(tasks)

    asyncio.run(main())
