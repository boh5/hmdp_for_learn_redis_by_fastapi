"""
    voucher
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/25
"""
from sqlmodel import Session

import models
import schemas
from db.mysql import engine


class VoucherCRUD:
    def create(self, model: models.Voucher):
        with Session(engine) as sess:
            sess.add(model)
            sess.commit()
            sess.refresh(model)
        return model

    def create_seckill(self, model: schemas.SeckillVoucherCreateModel):
        voucher = models.Voucher.parse_obj(model)
        seckill_voucher = models.SeckillVoucher.parse_obj(model)
        with Session(engine) as sess:
            try:
                sess.add(voucher)
                sess.commit()
                seckill_voucher.voucher_id = voucher.id
                sess.add(seckill_voucher)
                sess.commit()
                sess.refresh(voucher)
                sess.refresh(seckill_voucher)
            except Exception:
                sess.rollback()

        return voucher, seckill_voucher


voucher_crud = VoucherCRUD()
