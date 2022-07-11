"""
    config
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY = 'abc123'

    MYSQL_HOST: str = 'localhost'
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = 'root'
    MYSQL_PASSWORD: str = 'root'
    MYSQL_DATABASE: str = 'hmdp'

    MAX_PAGE_SIZE: int = 10

    USER_NICK_NAME_PREFIX = 'user_'

    REDIS_HOST: str = '192.168.31.57'
    LOGIN_CODE_KEY_PREFIX: str = 'hmdp:login:code:'
    LOGIN_CODE_EXPIRE: int = 2 * 60
    LOGIN_USER_OBJ_KEY_PREFIX: str = 'hmdp:login:user:'
    LOGIN_USER_OBJ_EXPIRE: int = 30 * 60


settings = Settings()
