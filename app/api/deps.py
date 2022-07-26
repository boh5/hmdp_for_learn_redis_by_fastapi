"""
    deps
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
from typing import Optional

from fastapi import HTTPException, Header
from starlette import status
from starlette.requests import Request

import models
import schemas
from core.config import settings
from utils.redis import aio_redis, get_login_user_obj_key


async def verify_user(authorization: str = Header()) -> schemas.UserBaseModel:
    user_dict = await aio_redis.hgetall(get_login_user_obj_key(authorization))
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = schemas.UserBaseModel.parse_obj(user_dict)
    return user


async def refresh_user_obj_in_redis(authorization: Optional[str] = Header(default=None)):
    if authorization:
        is_key_exists = await aio_redis.exists(get_login_user_obj_key(authorization))
        if is_key_exists:
            await aio_redis.expire(get_login_user_obj_key(authorization), settings.LOGIN_USER_OBJ_EXPIRE)
