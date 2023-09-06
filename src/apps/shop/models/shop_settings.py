from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from common.singleton import SingletonModel


class ShopSettings(SingletonModel):
    """ Allows to set global settings using the admin interface
    """
    vat_percent = models.DecimalField(
        _("VAT"),
        help_text=("In percent"),
        max_digits=2,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    default_coupon_code_length = models.PositiveSmallIntegerField(
        verbose_name=_('Coupon code default length'),
        default=8,
    )

    default_coupon_validity_in_days = models.PositiveSmallIntegerField(
        verbose_name=_('Coupon default validity in days'),
        default=365,
    )

    coupon_code_characters = models.CharField(
        verbose_name=_('Coupon default used characters'),
        help_text=_('Any lower case letters will be capitalized, avoid duplicate characters'),
        default='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        max_length=64,
    )

    class Meta:
        verbose_name_plural = " Settings"  # The space is a hack so this model's admin occupies the first place

    def save(self, *args, **kwargs):
        """ override """
        self.coupon_code_characters = self.coupon_code_characters.upper()
        super().save(*args, **kwargs)