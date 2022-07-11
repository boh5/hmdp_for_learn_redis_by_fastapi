"""
    mysql
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
from sqlmodel import create_engine

from core.config import settings

engine = create_engine(
    f'mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}'
    f':{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}')
