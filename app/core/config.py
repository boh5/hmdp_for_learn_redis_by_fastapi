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


settings = Settings()
