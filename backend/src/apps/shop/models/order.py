import random
from decimal import Decimal

from django.apps import apps
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from . import ShopSettings


class Order(models.Model):

    order_number = models.PositiveIntegerField(editable=False, unique=True, db_index=True)
    cart = models.OneToOneField("shop.Cart", on_delete=models.CASCADE)
    billing_info = models.OneToOneField("shop.BillingInfo", on_delete=models.PROTECT, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    order_placed = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    base_total = models.DecimalField(editable=False, max_digits=8, decimal_places=2, default=0)
    gross_total = models.DecimalField(editable=False, max_digits=8, decimal_places=2, default=0)
    net_total = models.DecimalField(editable=False, max_digits=8, decimal_places=2, default=0)
    vat_total = models.DecimalField(editable=False, max_digits=8, decimal_places=2, default=0)

    @property
    def discount_total(self):
        return self.base_total - self.gross_total

    @property
    def billing_info_str(self):
        return str(self.billing_info.__str__())

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return str(self.order_number)

    def get_absolute_url(self):
        return reverse("Order_detail", kwargs={"pk": self.pk})

    def _generate_and_set_order_number(self):
        while True:
            candidate_order_number = random.randint(
                ShopSettings.load().order_number_lower_limit,
                ShopSettings.load().order_number_upper_limit,
            )
            if not Order.objects.filter(order_number=candidate_order_number).exists():
                # Found a unique order number
                self.order_number = candidate_order_number
                break

    def calculate_and_set_base_total(self):
        total = self.orderitem_set.aggregate(Sum('base_price'))['base_price__sum']
        self.base_total = total if total else 0

    def calculate_and_set_gross_total(self):
        total = self.orderitem_set.aggregate(Sum('gross_price'))['gross_price__sum']
        self.gross_total = total if total else 0

    def calculate_and_set_net_total(self):
        total = self.orderitem_set.aggregate(Sum('net_price'))['net_price__sum']
        self.net_total = total if total else 0

    def calculate_and_set_vat_total(self):
        self.vat_total = self.gross_total - self.net_total

    def add_item(self, *, reference: str, base_price: Decimal, gross_price: Decimal, vat_factor: Decimal):
        OrderItem = apps.get_model('shop', 'OrderItem')
        return OrderItem.objects.create(
            order=self,
            reference=reference,
            base_price=base_price,
            gross_price=gross_price,
            vat_factor=vat_factor,
        )

    def _create_associated_billing_info(self):
        BillingInfo = apps.get_model('shop', 'BillingInfo')
        self.billing_info = BillingInfo.objects.create()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self._generate_and_set_order_number()
        if not self.billing_info:
            self._create_associated_billing_info()
        super().save(*args, **kwargs)

