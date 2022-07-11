"""
    shop_type
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from fastapi import APIRouter

import crud
import schemas

router = APIRouter()


@router.get('/list',
            response_model=schemas.GenericResponseModel)
async def list_shop_type(

):
    results = crud.shop_type_crud.list_shop_type()
    data = [m.dict() for m in results]
    return schemas.GenericResponseModel(data=data)
