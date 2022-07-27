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

order_queue = queue.Queue(1024 * 1024)

IS_RUNNING = True
executor = concurrent.futures.ThreadPoolExecutor()


class VoucherOrderHandler:
    def __init__(self, task_queue: queue.Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue

    def __call__(self) -> None:
        while IS_RUNNING:
            try:
                voucher_order = self.task_queue.get(timeout=2)
            except queue.Empty:
                continue
            if voucher_order == signal.SIG_UNBLOCK:
                break
            user_id = voucher_order.user_id
            lock = redis.lock(name=settings.REDIS_LOCK_KEY_PREFIX + 'order:' + str(user_id),
                              timeout=10)
            try:
                is_lock = lock.acquire(blocking=False)
                if not is_lock:
                    print('不允许重复下单, lock false')
                self.create_voucher_order(voucher_order)
            except Exception as e:
                print(e)
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
    executor.submit(VoucherOrderHandler(order_queue))


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

    response = await aio_redis.eval(lua_script, 2,
                                    settings.CACHE_SECKILL_STOCK_KEY_PREFIX + str(voucher_id),
                                    settings.CACHE_SECKILL_ORDER_KEY_PREFIX + str(voucher_id),
                                    user.id)

    if response != 0:
        return schemas.GenericResponseModel(success=False,
                                            error_msg='库存不足' if response == 1 else '不能重复下单')

    order_id = await redis_id_worker.next_id('order:')

    # 保存阻塞队列
    voucher_order = models.VoucherOrder(
        id=order_id,
        user_id=user.id,
        voucher_id=voucher_id,
    )
    order_queue.put(voucher_order)

    return schemas.GenericResponseModel(data=order_id)
