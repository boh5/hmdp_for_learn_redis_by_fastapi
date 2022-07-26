"""
    lock
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/26
"""
import threading
import uuid

from aioredis import Redis

from core.config import settings


class SimpleRedisLock:
    def __init__(self, redis: Redis, name):
        self.redis = redis
        self.name = name
        self.key_prefix = settings.REDIS_LOCK_KEY_PREFIX
        self.key = self.key_prefix + self.name
        self.uuid = uuid.uuid4().hex
        self.value = self.uuid + '-' + str(threading.currentThread().ident)

    async def try_lock(self, timeout_sec) -> bool:
        success = await self.redis.set(self.key,
                                       self.value,
                                       ex=timeout_sec,
                                       nx=True)
        return success

    async def unlock(self):
        lua = """
            if (redis.call('get', KEYS[1]) == ARGV[1]) then
                return redis.call('del', KEYS[1])
            end
            return 0
        """
        success = await self.redis.eval(lua, 1, self.key, self.value)
        return success

