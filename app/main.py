"""
    main
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
import multiprocessing

from fastapi import FastAPI, Depends
from starsessions import SessionMiddleware, InMemoryBackend

from api.deps import refresh_user_obj_in_redis
from app.api.api import api_router
from core.config import settings

# app = FastAPI(dependencies=[Depends(refresh_user_obj_in_redis)])
app = FastAPI()


app.include_router(api_router, prefix='')

app.add_middleware(SessionMiddleware, backend=InMemoryBackend())
