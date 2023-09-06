
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import ProductGroupAppointment

class CartProduct(models.Model):
    cart = models.ForeignKey("shop.Cart", related_name="products", verbose_name=_("Cart"), on_delete=models.CASCADE)
    product = models.ForeignKey(
        "shop.Product",
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
    )

    @property
    def _calculate_price(self):
        base_price = self.product.base_price
        coupons = self.cart.coupons
        products_in_cart = self.cart.products

    def __str__(self) -> str:
        return str(self.cart.__str__()) + self.product.__str__()