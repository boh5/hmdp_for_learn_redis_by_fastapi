"""
    api
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/10
"""
from fastapi import APIRouter
from app.api.endpoints import blog, blog_comments, follow, shop, shop_type, upload, user, voucher, voucher_order

api_router = APIRouter()
api_router.include_router(blog.router, prefix='/blog')
api_router.include_router(blog_comments.router, prefix='/blog-comments')
api_router.include_router(follow.router, prefix='/follow')
api_router.include_router(shop.router, prefix='/shop')
api_router.include_router(shop_type.router, prefix='/shop-type')
api_router.include_router(upload.router, prefix='/upload')
api_router.include_router(user.router, prefix='/user')
api_router.include_router(voucher.router, prefix='/voucher')
api_router.include_router(voucher_order.router, prefix='/voucher-order')
