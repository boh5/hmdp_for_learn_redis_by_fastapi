"""
    shop
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/17
"""
from sqlmodel import Session, select

import models
from db.mysql import engine


class ShopCRUD:
    def get(self, pk: int) -> models.Shop:
        with Session(engine) as sess:
            statement = select(models.Shop).where(models.Shop.id == pk)
            shop = sess.exec(statement).first()
        return shop


shop_crud = ShopCRUD()
