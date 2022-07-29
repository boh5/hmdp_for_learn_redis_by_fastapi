"""
    shop
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/17
"""
from typing import List, Optional

from sqlmodel import Session, select, col

import models
from db.mysql import engine


class ShopCRUD:
    def get(self, pk: int) -> models.Shop:
        with Session(engine) as sess:
            statement = select(models.Shop).where(models.Shop.id == pk)
            shop = sess.exec(statement).first()
        return shop

    def get_by_id_in(self, ids: List[int]) -> List[Optional[models.Shop]]:
        with Session(engine) as sess:
            shops = sess.exec(
                select(models.Shop).where(col(models.Shop.id).in_(ids))
            ).all()
        return shops


shop_crud = ShopCRUD()
