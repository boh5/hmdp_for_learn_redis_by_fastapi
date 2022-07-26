"""
    voucher_order
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import asyncio
import datetime
import multiprocessing
import threading

from fastapi import APIRouter, Path, Depends
from sqlmodel import Session, select

import models
import schemas
from api import deps
from db.mysql import engine
from utils.redis_id import redis_id_worker

router = APIRouter()


@router.post('/seckill/{voucher_id}',
             response_model=schemas.GenericResponseModel)
async def seckill_voucher(
        *,
        voucher_id: int = Path(),
        user: schemas.UserBaseModel = Depends(deps.verify_user)
):
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

        if sk_voucher.stock < 1:
            return schemas.GenericResponseModel(success=False, error_msg='库存不足')

        voucher_order_order_or_resp = await create_voucher_order(voucher_id, user.id)

        if isinstance(voucher_order_order_or_resp, schemas.GenericResponseModel):
            return voucher_order_order_or_resp
        return schemas.GenericResponseModel(data=voucher_order_order_or_resp.id)


async def create_voucher_order(voucher_id, user_id):
    with Session(engine) as sess:
        try:
            exists_user_orders = sess.exec(
                select(models.VoucherOrder)
                .where(models.VoucherOrder.user_id == user_id)
                .where(models.VoucherOrder.voucher_id == voucher_id)
            ).all()
            if len(exists_user_orders) > 0:
                return schemas.GenericResponseModel(success=False, error_msg='已经购买过一次了')

            result = sess.exec("UPDATE tb_seckill_voucher "
                               "SET stock=stock-1 "
                               "WHERE voucher_id={} "
                               "AND stock>0".format(voucher_id))
            sess.commit()

            if result.rowcount != 1:
                return schemas.GenericResponseModel(success=False, error_msg='秒杀失败, update 失败')

            voucher_order = models.VoucherOrder(
                id=await redis_id_worker.next_id('order:'),
                user_id=user_id,
                voucher_id=voucher_id,
            )
            sess.add(voucher_order)

            sess.commit()
            sess.refresh(voucher_order)
            return voucher_order
        except Exception as e:
            sess.rollback()
            print(e)
            return schemas.GenericResponseModel(success=False, error_msg='秒杀失败')
