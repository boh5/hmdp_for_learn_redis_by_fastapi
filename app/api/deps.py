"""
    deps
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

import models


async def verify_user(request: Request) -> models.User:
    await request.session.load()
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
