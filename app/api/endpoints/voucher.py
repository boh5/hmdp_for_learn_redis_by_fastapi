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
        statement = select(models.Voucher).where(models.Voucher.shop_id == shop_id)
        results = sess.exec(statement).all()

    data = [m.dict(by_alias=True) for m in results]
    return schemas.GenericResponseModel(data=data)
