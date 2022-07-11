"""
    user
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import random
from typing import Optional

from fastapi import APIRouter, Path, Query, Depends
from sqlmodel import Session, select
from starlette.requests import Request

import crud
import models
from api import deps
from app import schemas
from core.config import settings
from db.mysql import engine

router = APIRouter()


@router.post('/code',
             response_model=schemas.GenericResponseModel)
async def send_code(
        *,
        request: Request,
        phone: int = Query(),
):
    code = ''.join(random.sample(list(map(str, range(0, 10))), 6))
    await request.session.load()
    request.session.update({'code': code})
    print('发送验证码成功，验证码：{}'.format(code))
    return schemas.GenericResponseModel()


@router.post('/login',
             response_model=schemas.GenericResponseModel)
async def login(
        *,
        request: Request,
        login_model: schemas.UserLoginModel,
):
    await request.session.load()
    cached_code = request.session.get('code')
    if login_model.code is None or cached_code != login_model.code:
        return schemas.GenericResponseModel(success=False, error_msg='验证码错误')

    user = crud.user_crud.get_user_by_phone(phone=login_model.phone)
    if user is None:
        user = crud.user_crud.create_user_with_phone(phone=login_model.phone)

    request.session.update({'user': user})
    return schemas.GenericResponseModel()


@router.post('/logout',
             response_model=schemas.GenericResponseModel)
async def logout(
        *,
        user: models.User = Depends(deps.verify_user),
):
    pass


@router.get('/me',
            response_model=schemas.GenericResponseModel)
async def me(
        *,
        user: models.User = Depends(deps.verify_user),

):
    return schemas.GenericResponseModel(data=schemas.UserBaseModel.parse_obj(user))
