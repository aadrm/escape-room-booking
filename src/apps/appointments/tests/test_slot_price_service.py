from django.utils import timezone
from django.utils.timezone import timedelta

from apps.appointments.models import Slot, Room
from apps.appointments.services import SlotAvailabilityService, SlotPriceService
from apps.shop.models import Cart, ProductGroupAppointment, Product
from apps.shop.services import CartToOrderService
from .test_slot import BaseSlotTestCase

class TestSlotAvailabilityCase(BaseSlotTestCase):

    def setUp(self):
        super().setUp()
        self.cart = Cart.objects.create()
        self.product_group = ProductGroupAppointment.objects.create(name='group', room=self.room1)
        self.product_group_2 = ProductGroupAppointment.objects.create(name='group', room=self.room1)
        self.product = Product.objects.create(name="product", product_group=self.product_group, base_price=10)
        self.product_2 = Product.objects.create(name="product", product_group=self.product_group, base_price=2)
        self.product_3 = Product.objects.create(name="product", product_group=self.product_group_2, base_price=1)
        self.slot.start = timezone.now() + timedelta(hours=1)
        self.slot.save()
        self.preceding_slot_1 = Slot.objects.create(
            start=timezone.now(),
            duration=30,
            buffer=30,
            room=self.room1,
        )
        self.preceding_slot_2 = Slot.objects.create(
            start=timezone.now() + timedelta(minutes=15),
            duration=30,
            buffer=30,
            room=self.room2,
        )
        self.parallel_slot = Slot.objects.create(
            start=timezone.now() + timedelta(hours=1, minutes=15),
            duration=30,
            buffer=30,
            room=self.room2,
        )
        self.following_slot_1 = Slot.objects.create(
            start=timezone.now() + timedelta(hours=2),
            duration=30,
            buffer=30,
            room=self.room1,
        )
        self.following_slot_2 = Slot.objects.create(
            start=timezone.now() + timedelta(hours=2, minutes=15),
            duration=30,
            buffer=30,
            room=self.room2,
        )

    def test_get_slot_lowest_base_price(self):
        self.assertAlmostEqual(1, SlotPriceService.get_slot_lowest_base_price(self.slot))

    def test_get_slot_incentive_discount_parallel(self):
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        CartToOrderService.cart_to_order(self.cart)
        self.assertAlmostEqual(5, SlotPriceService.get_slot_incentive_discount(self.slot))

    def test_get_slot_incentive_discount_preceding(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_2)
        CartToOrderService.cart_to_order(self.cart)
        self.assertAlmostEqual(2, SlotPriceService.get_slot_incentive_discount(self.slot))

    def test_get_slot_incentive_discount_following(self):
        self.cart.add_item_appointment(self.product, self.following_slot_2)
        CartToOrderService.cart_to_order(self.cart)
        self.assertAlmostEqual(2, SlotPriceService.get_slot_incentive_discount(self.slot))

    def test_get_slot_incentive_discount_not_applicable(self):
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        self.assertAlmostEqual(0, SlotPriceService.get_slot_incentive_discount(self.slot))