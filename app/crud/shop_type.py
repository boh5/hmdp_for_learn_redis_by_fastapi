"""
    shop_type
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/11
"""
from sqlmodel import Session, select

import models
from db.mysql import engine


class ShopTypeCRUD:
    def list_shop_type(self):
        with Session(engine) as sess:
            statement = select(models.ShopType).order_by(models.ShopType.sort)
            results = sess.exec(statement).all()
        return results

shop_type_crud = ShopTypeCRUD()