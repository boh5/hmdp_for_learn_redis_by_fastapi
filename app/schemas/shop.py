"""
    shop
    ~~~

    

    :author: dilless(Huangbo)
    :date: 2022/7/29
"""
from typing import Optional

from pydantic import Field

import models


class ShopWithDistanceModel(models.Shop):
    distance: Optional[float] = Field(None)
