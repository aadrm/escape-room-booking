from django.db import models
from django.utils.translation import gettext_lazy as _


class CartItem(models.Model):
    cart = models.ForeignKey("shop.Cart", verbose_name=_("Cart"), on_delete=models.CASCADE)
    product = models.ForeignKey(
        "shop.Product",
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
    )

    # @property
    # def base_price(self) -> Decimal:
    #     return Decimal(self.product.base_price)

    # @property
    # def vat_factor(self) -> Decimal:
    #     return Decimal(self.product.vat_factor)

    # @property
    # def price(self) -> Decimal:
    #     return CartItemPriceCalculatorService.calculate_price(self)

    def __str__(self) -> str:
        return (
            str(self.cart.__str__()) +
            ' - ' +
            self.product.__str__()
        )
