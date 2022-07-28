"""
    user
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
import random
import string
from typing import Optional

from sqlmodel import Session, select

import models
from core.config import settings
from db.mysql import engine


class UserCRUD:
    def get_by_id(self, pk: int) -> Optional[models.User]:
        with Session(engine) as sess:
            statement = select(models.User).where(models.User.id == pk)
            result = sess.exec(statement).first()
        return result

    def get_user_by_phone(self, phone: str) -> Optional[models.User]:
        with Session(engine) as sess:
            statement = select(models.User).where(models.User.phone == phone)
            result = sess.exec(statement).one_or_none()
        return result

    def create_user_with_phone(self, phone: str) -> models.User:
        with Session(engine) as sess:
            user = models.User(phone=phone,
                               nick_name=settings.USER_NICK_NAME_PREFIX + ''.join(random.sample(string.hexdigits, 10)))
            sess.add(user)
            sess.commit()
            sess.refresh(user)
        return user


user_crud = UserCRUD()
