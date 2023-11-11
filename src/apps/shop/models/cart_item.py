from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from ..utils.cart_item_price_calculation_service import CartItemPriceCalculatorService


class CartItem(models.Model):
    cart = models.ForeignKey("shop.Cart", verbose_name=_("Cart"), on_delete=models.CASCADE)
    product = models.ForeignKey(
        "shop.Product",
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
    )

    @property
    def base_price(self) -> Decimal:
        return Decimal(self.product.base_price)

    @property
    def price(self) -> Decimal:
        coupons_in_cart = self.cart.coupons.all().order_by('coupon__is_percent')
        items_in_cart = self.cart.cartitem_set.all()
        return CartItemPriceCalculatorService.calculate_price(self, coupons_in_cart, items_in_cart)

    def __str__(self) -> str:
        return (
            str(self.cart.__str__()) +
            ' - ' +
            self.product.__str__() +
            ' - ' +
            str(self.price)
        )
