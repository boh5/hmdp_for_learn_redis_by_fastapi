"""
    follow
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/28
"""
import random
import string
from typing import Optional

from sqlmodel import Session, select

import models
from core.config import settings
from db.mysql import engine


class FollowCRUD:
    def get_fan_ids(self, user_id: int):
        with Session(engine) as sess:
            follow_user_ids = sess.exec(
                select(models.Follow.user_id, ).where(models.Follow.follow_user_id == user_id)
            ).all()
        return follow_user_ids


follow_crud = FollowCRUD()

if __name__ == '__main__':
    ans = follow_crud.get_fan_ids(2)
    print(ans)
