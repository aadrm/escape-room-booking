from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):

    name = models.CharField(_("Name"), max_length=32)
    base_price = models.DecimalField(_("Price"), max_digits=5, decimal_places=2)
    product_group = models.ForeignKey("shop.ProductGroup", verbose_name=_("Group"), on_delete=models.CASCADE)
    is_purchaseable = models.BooleanField(
        _("Is purchaseable"),
        help_text=_('Whether the product is selectable by the public'),
        default=True,
    )

    class Meta:
        ordering = ['base_price']

    def __str__(self) -> str:
        return self.name

