"""
    redis
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import aioredis

from core.config import settings

redis = aioredis.from_url(f'redis://{settings.REDIS_HOST}', decode_responses=True)


def get_login_code_key(phone: str) -> str:
    return settings.LOGIN_CODE_KEY_PREFIX + phone


def get_login_user_obj_key(token: str) -> str:
    return settings.LOGIN_USER_OBJ_KEY_PREFIX + token
