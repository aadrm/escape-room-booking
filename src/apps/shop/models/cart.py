
from django.apps import apps
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.appointments.models import Slot
from . import CartItemAppointment, CartItemCoupon


class Cart(models.Model):


    class Status(models.IntegerChoices):
        OPEN = 1
        COMPLETED = 2
        CANCELLED = 3

    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.OPEN)

    def __str__(self) -> str:
        return str(self.pk)

    def is_slot_blocking(self):
        return self.status in [self.Status.OPEN, self.Status.COMPLETED]

    def get_coupons(self):
        Coupon = apps.get_model('shop', 'Coupon')
        coupon_ids = self.coupons.values('coupon')
        return Coupon.objects.filter(pk__in=coupon_ids)


    def add_coupon(self, coupon) -> None:
        Coupon = apps.get_model('shop', 'Coupon')
        CartCoupon = apps.get_model('shop', 'CartCoupon')

        if coupon not in self.get_coupons():
            CartCoupon.objects.create(
                cart=self,
                coupon=coupon
            )

    def get_slots(self):
        slot_ids = self.get_cartitemappointment_set().values('slot')
        return Slot.objects.filter(pk__in=slot_ids)

    def get_cartitemappointment_set(self):
        return CartItemAppointment.objects.filter(cart=self)

    def get_cartitemcoupon_set(self):
        return CartItemCoupon.objects.filter(cart=self)

    def add_item_appointment(self, product, slot) -> None:
        Product = apps.get_model('shop', 'Product')
        Slot = apps.get_model('appointments', 'Slot')
        CartItemAppointment = apps.get_model('shop', 'CartItemAppointment')
        if slot.is_available_to_staff():
            CartItemAppointment.objects.create(
                cart=self,
                product=product,
                slot=slot,
            )

    def add_item_coupon(self, product) -> None:
        Product = apps.get_model('shop', 'Product')
        CartItemCoupon = apps.get_model('shop', 'CartItemCoupon')

        CartItemCoupon.objects.create(
            cart=self,
            product=product,
        )