"""
    voucher
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from typing import Optional

from fastapi import APIRouter, Path, Query
from sqlmodel import Session, select
from starlette.requests import Request

import crud
import models
from app import schemas
from core.config import settings
from db.mysql import engine

router = APIRouter()


@router.get('/list/{shop_id}',
            response_model=schemas.GenericResponseModel)
async def query_voucher_of_shop(
        *,
        shop_id: int = Path,
):
    with Session(engine) as sess:
        statement = select(models.Voucher, models.SeckillVoucher) \
            .join(models.SeckillVoucher, models.Voucher.id == models.SeckillVoucher.voucher_id, isouter=True) \
            .where(models.Voucher.shop_id == shop_id)
        results = sess.exec(statement).all()

    data = []
    for voucher, seckill_voucher in results:
        d = voucher.dict()
        if seckill_voucher:
            d.update(**seckill_voucher.dict(exclude={'create_time', 'update_time'}))
        data.append(schemas.SeckillVoucherModel.parse_obj(d).dict(exclude_unset=True, by_alias=True))
    return schemas.GenericResponseModel(data=data)


@router.post('',
             response_model=schemas.GenericResponseModel)
async def add_voucher(
        *,
        model: models.Voucher,
):
    model = crud.voucher_crud.create(model)
    return schemas.GenericResponseModel(data=model.id)


@router.post('/seckill',
             response_model=schemas.GenericResponseModel)
async def add_seckill_voucher(
        *,
        model: schemas.SeckillVoucherCreateModel,
):
    model = crud.voucher_crud.create_seckill(model)
    return schemas.GenericResponseModel(data=model.id)
