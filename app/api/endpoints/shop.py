"""
    shop
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


@router.get('/{id}',
            response_model=schemas.GenericResponseModel)
async def query_shop_by_id(
        *,
        id: int = Path
):
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.id == id)
        result = sess.exec(statement).one()

    return schemas.GenericResponseModel(data=result.dict(by_alias=True))


@router.get('/of/type',
            response_model=schemas.GenericResponseModel)
async def query_shop_by_type(
        *,
        type_id: int = Query(alias='typeId'),
        page: int = Query(alias='current')
):
    if page <= 0:
        page = 1
    with Session(engine) as sess:
        statement = select(models.Shop).where(models.Shop.type_id == type_id).limit(settings.MAX_PAGE_SIZE).offset(
            page * settings.MAX_PAGE_SIZE - settings.MAX_PAGE_SIZE)
        results = sess.exec(statement).all()
    data = [r.dict(by_alias=True) for r in results]
    return schemas.GenericResponseModel(data=data)
