from django.db import models
from django.utils.translation import gettext_lazy as _

from . import ProductGroup


class ProductGroupCoupon(ProductGroup):

    shipping_cost = models.DecimalField(_("Shipping cost"), max_digits=5, decimal_places=2)

