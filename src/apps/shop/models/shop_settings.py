from django.db import models
from django.utils.translation import gettext_lazy as _
from common.singleton import SingletonModel

class ShopSettings(SingletonModel):
    """ Allows to set global settings using the admin interface
    """

    default_coupon_code_length = models.PositiveSmallIntegerField(
        verbose_name=_('Coupon code default length'),
        default=8,
    )

    default_coupon_validity_in_days = models.PositiveSmallIntegerField(
        verbose_name=_('Coupon default validity in days'),
        default=365,
    )

    default_coupon_code_chars = models.SlugField(
        verbose_name=_('Coupon default used characters'),
        help_text=_('Any lower case letters will be capitalized, avoid duplicate characters'),
        default='ABCDEFHJKMNPQRSTWXYZ123489',
        max_length=32,
    )

    slot_set_aside_time = models.PositiveSmallIntegerField(
        verbose_name=_("Slot set aside time"),
        help_text=_('Time that a slot is reserved after added to the cart'),
        default=20,
    )

    order_number_lower_limit = models.PositiveIntegerField(
        verbose_name="Order number smallest possible value",
        help_text="Order numbers are a randomly generated number with at least this value",
        default=100000,
    )

    order_number_upper_limit = models.PositiveIntegerField(
        verbose_name="Order number largest possible value",
        help_text="Order numbers are a randomly generated number with this value at the most",
        default=999999,
    )

    min_order_number_separation = 100000

    class Meta:
        verbose_name_plural = " Settings"  # The space is a hack so this model's admin occupies the first place

    def save(self, *args, **kwargs):
        """ override """
        self.default_coupon_code_chars = self.default_coupon_code_chars.upper()
        if self.order_number_upper_limit <= self.order_number_lower_limit + self.min_order_number_separation:
            self.order_number_upper_limit = self.order_number_lower_limit + self.min_order_number_separation
        super().save(*args, **kwargs)