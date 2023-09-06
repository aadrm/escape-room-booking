from datetime import datetime, timedelta
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from common.days_of_week_mixin import DaysOfWeekMixin

from . import ShopSettings


def default_expiry_calc():
    return datetime.now() + timedelta(days=ShopSettings.load().default_coupon_validity_in_days)


class Coupon(models.Model, DaysOfWeekMixin):
    reference = models.CharField(_("Reference"), max_length=50)
    code = models.SlugField(
        "Code",
        blank=True,
        max_length=32,
    )
    value = models.DecimalField(
        _("Value"),
        decimal_places=2,
        default=0,
        max_digits=5,
    )
    is_percent = models.BooleanField(
        _("Is percent"),
        default=False,
        help_text=_("Type of coupon, absolute value or percent"),
    )
    apply_to_entire_cart = models.BooleanField(
        _("Applies to entire cart"),
        default=False,
        help_text=_("Whether the coupon is applied to the entire cart or a single item"),
    )
    minimum_spend = models.DecimalField("Minimum spend", max_digits=5, decimal_places=2, default=0)
    combines = models.BooleanField(
        _("Combinable"),
        default=False,
        help_text=("Allows the use of several coupons in a single cart"),
    )
    product_included = models.ManyToManyField(
        "shop.Product",
        help_text=_("If empty its applicable to all products"),
        related_name="product_include",
        verbose_name="include products",
        blank=True,
    )
    use_counter = models.IntegerField("Use courter", default=0)
    use_limit = models.IntegerField("Usage limit", default=1)
    created = models.DateTimeField("Created", auto_now=True, auto_now_add=False)
    expiry = models.DateField('Expiration date', blank=True, null=True, default=default_expiry_calc)
    days_of_week = models.CharField(
        max_length=50,
        default='[0, 1, 2, 3, 4, 5 ,6]',
    )

    def _random_coupon_code(self):
        allowed_chars = ShopSettings.load().coupon_code_characters
        this_class = type(self)
        existing_coupons = this_class.objects.all().exclude(pk=self.pk)
        while True:  # keep checking until we have a valid slug
            new_code = get_random_string(ShopSettings.load().default_coupon_code_length, allowed_chars).upper()
            duplicate_coupons = existing_coupons.filter(code=new_code)
            if not duplicate_coupons:
                return new_code

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        if not self.code:
            self.code = self._random_coupon_code()
        self.code = self.code.upper()
        super(Coupon, self).save(*args, **kwargs)