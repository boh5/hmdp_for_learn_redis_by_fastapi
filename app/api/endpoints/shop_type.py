"""
    shop_type
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import json
from typing import List

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as

import crud
import models
import schemas
from core.config import settings
from utils.redis_ import aio_redis, get_cache_shop_type_list_key

router = APIRouter()


@router.get('/list',
            response_model=schemas.GenericResponseModel)
async def list_shop_type(

):
    shop_type_list_str = await aio_redis.get(get_cache_shop_type_list_key())
    if not shop_type_list_str:
        shop_type_obj_list = crud.shop_type_crud.list_shop_type()
        await aio_redis.setex(get_cache_shop_type_list_key(), settings.CACHE_EXPIRE,
                              json.dumps(jsonable_encoder(shop_type_obj_list)))
    else:
        print('list_shop_type 没用打到 mysql ')
        shop_type_obj_list = parse_obj_as(List[models.ShopType], json.loads(shop_type_list_str))
    data = [m.dict() for m in shop_type_obj_list]
    return schemas.GenericResponseModel(data=data)
