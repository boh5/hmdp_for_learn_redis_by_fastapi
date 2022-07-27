"""
    user
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import asyncio
import hashlib
import random
import uuid
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
from utils.redis_ import aio_redis, get_login_code_key, get_login_user_obj_key

router = APIRouter()


@router.post('/code',
             response_model=schemas.GenericResponseModel)
async def send_code(
        *,
        phone: str = Query(),
):
    code = ''.join(random.sample(list(map(str, range(0, 10))), 6))
    await aio_redis.setex(get_login_code_key(phone), settings.LOGIN_CODE_EXPIRE, code)
    print('发送验证码成功，验证码：{}'.format(code))
    return schemas.GenericResponseModel()


@router.post('/login',
             response_model=schemas.GenericResponseModel)
async def login(
        *,
        login_model: schemas.UserLoginModel,
):
    cached_code = await aio_redis.get(get_login_code_key(login_model.phone))
    if login_model.code is None or cached_code != login_model.code:
        return schemas.GenericResponseModel(success=False, error_msg='验证码错误')

    user = crud.user_crud.get_user_by_phone(phone=login_model.phone)
    if user is None:
        user = crud.user_crud.create_user_with_phone(phone=login_model.phone)

    token = hashlib.md5(str(user.id).encode()).hexdigest()
    base_user = schemas.UserBaseModel.parse_obj(user)
    await aio_redis.hmset(get_login_user_obj_key(token), base_user.dict(exclude_none=True))
    await aio_redis.expire(get_login_user_obj_key(token), settings.LOGIN_USER_OBJ_EXPIRE)

    return schemas.GenericResponseModel(data=token)


@router.post('/logout',
             response_model=schemas.GenericResponseModel)
async def logout(
        *,
        user: schemas.UserBaseModel = Depends(deps.verify_user),
):
    pass


@router.get('/me',
            response_model=schemas.GenericResponseModel)
async def me(
        *,
        user: schemas.UserBaseModel = Depends(deps.verify_user),

):
    return schemas.GenericResponseModel(data=schemas.UserBaseModel.parse_obj(user))


if __name__ == '__main__':
    async def do_job(u, lock):
        code = await send_code(phone=u.phone)
        login_obj = schemas.UserLoginModel(
            phone=u.phone,
            code=code,
        )
        login_resp = await login(login_model=login_obj)
        token = login_resp.data
        async with lock:
            with open('../../../token.txt', 'a', encoding='utf-8') as f:
                f.write(token + '\n')


    async def main():
        with Session(engine) as sess:
            users = sess.exec(select(models.User)).all()[:1000]
        lock = asyncio.Lock()
        for u in users:
            await do_job(u, lock)


    asyncio.run(main())
