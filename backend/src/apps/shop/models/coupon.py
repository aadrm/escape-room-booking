from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from common.days_of_week_mixin import DaysOfWeekMixin

from . import ShopSettings


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
    products_included = models.ManyToManyField(
        "shop.Product",
        help_text=_("If empty its applicable to all products"),
        related_name="product_include",
        verbose_name="include products",
        blank=True,
    )
    use_counter = models.IntegerField("Use courter", default=0)
    use_limit = models.IntegerField("Usage limit", default=1)
    created = models.DateField("Created", auto_now=True, auto_now_add=False)
    days_valid = models.PositiveIntegerField('Expiration date', default=365)
    days_of_week = models.CharField(
        max_length=50,
        default='[0, 1, 2, 3, 4, 5 ,6]',
    )

    @property
    def is_depleted(self) -> bool:
        return self.use_counter >= self.use_limit

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expiration_date

    @property
    def is_available(self) -> bool:
        return not self.is_expired and not self.is_depleted

    @property
    def expiration_date(self) -> timezone.datetime:
        return self.created + timezone.timedelta(days=self.days_valid)

    def count_use(self) -> None:
        self.use_counter = self.use_counter + 1
        self.save()

    def generate_code_if_empty(self):
        if not self.code:
            code = self._random_coupon_code().upper()
            self.code = code


    def _random_coupon_code(self) -> str:
        allowed_chars = ShopSettings.load().default_coupon_code_chars
        this_class = type(self)
        existing_coupons = this_class.objects.all().exclude(pk=self.pk)
        while True:  # keep checking until we have a valid slug
            new_code = get_random_string(ShopSettings.load().default_coupon_code_length, allowed_chars).upper()
            duplicate_coupons = existing_coupons.filter(code=new_code)
            if not duplicate_coupons:
                return new_code

    def _applicable_products(self):
        if self.products_included.exists():
            return self.products_included.all()
        else:
            return self.products_included.model.objects.all()

    def is_applicable_to_product(self, product) -> bool:
        return product in self._applicable_products()

    def is_applicable_to_slot(self, slot) -> bool:
        return

    def is_applicable_to_item(self, item) -> bool:
        return True
        if not self.is_applicable_to_product(item.product):
            return False
        if not self.is_applicable_to_slot(item.slot):
            return False


    def calculate_discounted_price(self, value: Decimal) -> Decimal:
        if self.is_percent:
            factor = (1 - self.value / 100)
            value = value * factor
            return value
        else:
            return max(value - self.value, 0)

    def set_default_validity(self):
        self.days_valid = ShopSettings.load().default_coupon_validity_in_days

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        self.generate_code_if_empty()
        if self.pk is None:
            self.set_default_validity()
        super(Coupon, self).save(*args, **kwargs)

