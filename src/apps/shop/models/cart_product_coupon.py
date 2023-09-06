
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import CartProduct


class CartProductCoupon(CartProduct):
    coupon = models.ForeignKey("shop.Coupon", verbose_name=_("coupon"), on_delete=models.CASCADE)


    def __str__(self) -> str:
        return super().__str__() + self.coupon.__str__()