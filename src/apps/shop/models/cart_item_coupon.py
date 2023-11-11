
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import CartItem


class CartItemCoupon(CartItem):
    coupon = models.ForeignKey("shop.Coupon", verbose_name=_("coupon"), on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self) -> str:
        return super().__str__() + self.coupon.__str__()