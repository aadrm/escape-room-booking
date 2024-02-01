from django.apps import apps
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from apps.appointments.models import Slot
from apps.appointments.services import SlotAvailabilityService
from . import CartItemAppointment, CartItemCoupon


class Cart(models.Model):

    def __str__(self) -> str:
        return str(self.pk)

    def get_absolute_url(self):
        return reverse('admin:shop_cart_change', args=[self.pk])

    def is_open(self):
        return not hasattr(self, 'order')

    def is_completed(self):
        if hasattr(self, 'order'):
            return not self.order.is_cancelled
        return False

    def is_slot_blocking(self):
        return self.is_open or self.is_completed

    def get_total_base_price(self):
        items = self.get_cartitem_set()
        total_base_price = items.aggregate(base_price=Sum('product__base_price'))['base_price']
        return total_base_price

    def get_coupons(self):
        Coupon = apps.get_model('shop', 'Coupon')
        coupon_ids = self.coupons.values('coupon')
        return Coupon.objects.filter(pk__in=coupon_ids)

    def add_coupon(self, coupon) -> None:
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
        self.clean_expired_appointment_items()
        # can't use self.cartitemappointment_set because the relationship is to the CartItem object
        return CartItemAppointment.objects.filter(cart=self)

    def get_cartitemcoupon_set(self):
        # can't use self.cartitemappointment_set because the relationship is to the CartItem object
        return CartItemCoupon.objects.filter(cart=self)

    def get_cartitem_set(self):
        self.clean_expired_appointment_items()
        return self.cartitem_set.all()

    def clean_expired_appointment_items(self):
        appointment_item_set = CartItemAppointment.objects.filter(cart=self)
        appointment_items_to_delete = [appointment.pk for appointment in appointment_item_set if appointment.is_expired()]
        appointment_item_set.filter(pk__in=appointment_items_to_delete).delete()

    def add_item_appointment(self, product, slot) -> CartItemAppointment:
        """adds an ItemAppointment to the class

        Args:
            product (Product): The product that's added
            slot (Slot): The related slot

        Returns:
            CartItemAppointment: returns the newly created CartItemAppointment
        """
        CartItemAppointment = apps.get_model('shop', 'CartItemAppointment')
        # The only condition that needs to be passed is that the appointment to the cart
        # is still available to the staff. Any limitations to the end customer
        # should be taken care of in the front end.
        if not SlotAvailabilityService.is_unavailable(slot):
            return CartItemAppointment.objects.create(
                cart=self,
                product=product,
                slot=slot,
            )

    def add_item_coupon(self, product) -> CartItemCoupon:
        """Adds a CartItemCoupon to the cart and returns it

        Args:
            product (Product):

        Returns:
            CartItemCoupon: The newly created CartItemCoupon
        """
        Product = apps.get_model('shop', 'Product')
        CartItemCoupon = apps.get_model('shop', 'CartItemCoupon')

        return CartItemCoupon.objects.create(
            cart=self,
            product=product,
        )