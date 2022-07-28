"""
    voucher_order
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import asyncio
import concurrent.futures
import datetime
import multiprocessing
import queue
import signal
import threading
import time

import pottery
from fastapi import APIRouter, Path, Depends
from sqlmodel import Session, select

import models
import schemas
from api import deps
from core.config import settings
from db.mysql import engine
from utils.lock import SimpleRedisLock
from utils.redis_ import aio_redis, redis
from utils.redis_id import redis_id_worker

router = APIRouter()

IS_RUNNING = True
executor = concurrent.futures.ThreadPoolExecutor()


class VoucherOrderHandler:
    stream_name = 'stream.orders'
    group_name = 'g1'

    def __call__(self) -> None:
        while IS_RUNNING:
            voucher_orders = redis.xreadgroup(self.group_name, 'c1', {self.stream_name: '>'}, 1, 2000)
            if not voucher_orders:
                continue
            voucher_order_dict = voucher_orders[0][1][0][1]
            stream_message_id = voucher_orders[0][1][0][0]
            voucher_order = models.VoucherOrder.parse_obj(voucher_order_dict)
            user_id = voucher_order.user_id
            lock = redis.lock(name=settings.REDIS_LOCK_KEY_PREFIX + 'order:' + str(user_id),
                              timeout=10)
            try:
                is_lock = lock.acquire(blocking=False)
                if not is_lock:
                    print('不允许重复下单, lock false')
                self.create_voucher_order(voucher_order)
            except Exception as e:
                self.handel_pending_list()
                print(e)
            else:
                redis.xack(self.stream_name, self.group_name, stream_message_id)
            finally:
                if lock.locked():
                    lock.release()

    def handel_pending_list(self):
        while IS_RUNNING:
            voucher_orders = redis.xreadgroup(self.group_name, 'c1', {self.stream_name: '0'}, 1)
            if not voucher_orders:
                break
            voucher_order_dict = voucher_orders[0][1][0][1]
            stream_message_id = voucher_orders[0][1][0][0]
            voucher_order = models.VoucherOrder.parse_obj(voucher_order_dict)
            user_id = voucher_order.user_id
            lock = redis.lock(name=settings.REDIS_LOCK_KEY_PREFIX + 'order:' + str(user_id),
                              timeout=10)
            try:
                is_lock = lock.acquire(blocking=False)
                if not is_lock:
                    print('不允许重复下单, lock false, handle pending list')
                self.create_voucher_order(voucher_order)
            except Exception as e:
                print(e)
                time.sleep(.2)
            else:
                redis.xack(self.stream_name, self.group_name, stream_message_id)
            finally:
                if lock.locked():
                    lock.release()

    def create_voucher_order(self, voucher_order):
        user_id = voucher_order.user_id
        voucher_id = voucher_order.voucher_id
        with Session(engine) as sess:
            try:
                exists_user_orders = sess.exec(
                    select(models.VoucherOrder)
                    .where(models.VoucherOrder.user_id == user_id)
                    .where(models.VoucherOrder.voucher_id == voucher_id)
                ).all()
                if len(exists_user_orders) > 0:
                    raise RuntimeError('不允许重复下单, 已存在')

                result = sess.exec("UPDATE tb_seckill_voucher "
                                   "SET stock=stock-1 "
                                   "WHERE voucher_id={} "
                                   "AND stock>0".format(voucher_id))
                sess.commit()

                if result.rowcount != 1:
                    raise RuntimeError('秒杀失败, update 失败')

                sess.add(voucher_order)

                sess.commit()
                sess.refresh(voucher_order)
                return schemas.GenericResponseModel(data=voucher_order.id)
            except Exception as e:
                sess.rollback()
                print(e)
                raise RuntimeError('秒杀失败')


@router.on_event('startup')
async def run_voucher_order_handler():
    executor.submit(VoucherOrderHandler())


@router.on_event('shutdown')
async def shutdown_thread_pool_executor():
    global IS_RUNNING
    IS_RUNNING = False


@router.post('/seckill/{voucher_id}',
             response_model=schemas.GenericResponseModel)
async def seckill_voucher(
        *,
        voucher_id: int = Path(),
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
    lua_script = """
        -- seckill
        local stock_key = KEYS[1]
        local order_key = KEYS[2]
        
        local user_id = ARGV[1]
        local voucher_id = ARGV[2]
        local order_id = ARGV[3]
        
        -- 判断库存是否充足
        if (tonumber(redis.call('get', stock_key)) <= 0) then
            return 1
        end
        
        -- 是否已经秒杀了
        if (redis.call('sismember', order_key, user_id) == 1) then
            return 2
        end
        
        -- 到这说明可以下单
        redis.call('incrby', stock_key, -1)
        redis.call('sadd', order_key, user_id)
        -- 发送消息到队列
        redis.call('xadd', 'stream.orders', '*', 'user_id', user_id, 'voucher_id', voucher_id, 'id', order_id)
        return 0
    """
    with Session(engine) as sess:
        statement = select(models.SeckillVoucher).where(models.SeckillVoucher.voucher_id == voucher_id)
        sk_voucher = sess.exec(statement).first()
        now = datetime.datetime.now()

        if not sk_voucher:
            return schemas.GenericResponseModel(success=False, error_msg='优惠券不存在')

        if sk_voucher.begin_time > now:
            return schemas.GenericResponseModel(success=False, error_msg='秒杀尚未开始')

        if sk_voucher.end_time < now:
            return schemas.GenericResponseModel(success=False, error_msg='秒杀已经结束')

    order_id = await redis_id_worker.next_id('order:')

    response = await aio_redis.eval(lua_script, 2,
                                    settings.CACHE_SECKILL_STOCK_KEY_PREFIX + str(voucher_id),
                                    settings.CACHE_SECKILL_ORDER_KEY_PREFIX + str(voucher_id),
                                    user.id, voucher_id, order_id)

    if response != 0:
        return schemas.GenericResponseModel(success=False,
                                            error_msg='库存不足' if response == 1 else '不能重复下单')

    return schemas.GenericResponseModel(data=order_id)
