"""
    redis_id
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/25
"""
import datetime
import time

from aioredis import Redis

from utils.redis import aio_redis


class RedisIdWorker:
    BEGIN_TIMESTAMP = 1640995200
    COUNT_BITS = 32

    def __init__(self, redis: Redis):
        self.redis = redis

    async def next_id(self, key_prefix):
        # 生成时间戳
        now = datetime.datetime.now()
        now_timestamp = int(now.timestamp())
        timestamp = now_timestamp - self.BEGIN_TIMESTAMP

        # 生成序列号
        cur_date_str = now.strftime('%Y:%m:%d')
        count = await self.redis.incr('incr:' + key_prefix + cur_date_str)

        # 拼接并返回
        return timestamp << self.COUNT_BITS | count


redis_id_worker = RedisIdWorker(redis=aio_redis)

if __name__ == '__main__':
    import asyncio


    async def get_id(key_pre, sem):
        async with sem:
            result = await redis_id_worker.next_id(key_pre)
        return result


    async def main():
        tasks = []
        start = time.time()
        sem = asyncio.Semaphore(300)
        for i in range(30000):
            tasks.append(asyncio.create_task(get_id('test:', sem)))
        done, _ = await asyncio.wait(tasks)
        print('time cost:', time.time() - start)


    asyncio.run(main())
