
from django.db import models
from django.utils.translation import gettext_lazy as _


class CartCoupon(models.Model):
    cart = models.ForeignKey("shop.Cart", related_name='coupons', verbose_name=_("Cart"), on_delete=models.CASCADE)
    coupon = models.ForeignKey("shop.Coupon", verbose_name=_("Product"), on_delete=models.CASCADE)

