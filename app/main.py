"""
    main
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from fastapi import FastAPI
from starsessions import SessionMiddleware, InMemoryBackend

from app.api.api import api_router
from core.config import settings

app = FastAPI()

app.include_router(api_router, prefix='')

app.add_middleware(SessionMiddleware, backend=InMemoryBackend())
