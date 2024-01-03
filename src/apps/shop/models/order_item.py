from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class OrderItem(models.Model):

    reference = models.CharField("name", max_length=50)
    order = models.ForeignKey(
        "shop.Order",
        on_delete=models.CASCADE,
    )
    base_price = models.DecimalField(
        'base_price',
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    gross_price = models.DecimalField(
        'subtotal',
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    vat_factor = models.DecimalField(
        'vat_factor',
        max_digits=2,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))]
    )
    net_price = models.DecimalField(
        'net_price',
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        editable=False,
    )

    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"

    def __str__(self):
        return self.reference

    def set_net_price(self):
        self.net_price = Decimal(self.gross_price) / Decimal(1 + self.vat_factor)

    def save(self, *args, **kwargs):
        self.set_net_price()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("OrderItem_detail", kwargs={"pk": self.pk})

