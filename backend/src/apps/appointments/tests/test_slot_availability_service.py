from django.utils import timezone
from django.utils.timezone import timedelta

from apps.appointments.models import Slot
from apps.appointments.services import SlotAvailabilityService
from apps.shop.models import Cart, Product
from apps.shop.services import CartToOrderService
from .test_slot import BaseSlotTestCase


class TestSlotAvailabilityCase(BaseSlotTestCase):

    def setUp(self):
        super().setUp()
        self.cart = Cart.objects.create()
        self.product = Product.objects.create(name="product")
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

    def test_is_reserved(self):
        self.slot.start = timezone.now() + timedelta(days=1)
        self.cart.add_item_appointment(self.product, self.slot)
        self.assertEqual(True, SlotAvailabilityService.is_reserved(self.slot))

    def test_is_not_reserved(self):
        self.assertEqual(False, SlotAvailabilityService.is_reserved(self.slot))

    def test_is_booked(self):
        self.slot.start = timezone.now() + timedelta(days=1)
        self.cart.add_item_appointment(self.product, self.slot)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(True, SlotAvailabilityService.is_booked(self.slot))

    def test_is_blocked_by_buffer(self):
        self.slot.start = timezone.now() + timedelta(hours=1)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_buffer(self.slot))

    def test_is_not_affected_by_buffer(self):
        self.slot.start = timezone.now() + timedelta(hours=3, minutes=1)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_buffer(self.slot))

    def test_preceding_booked_slot_negates_buffer_effect(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_buffer(self.slot))

    def test_parallel_booked_slot_negates_buffer_effect(self):
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_buffer(self.slot))

    def test_is_blocked_by_booked_slots_two_preceding_one_parallel(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_2)
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_booked_adjacent_slots(self.slot))

    def test_is_blocked_by_booked_slots_two_following_one_parallel(self):
        self.cart.add_item_appointment(self.product, self.following_slot_1)
        self.cart.add_item_appointment(self.product, self.following_slot_2)
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_booked_adjacent_slots(self.slot))

    def test_is_not_blocked_by_booked_slots_two_preceding_two_following(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_2)
        self.cart.add_item_appointment(self.product, self.following_slot_1)
        self.cart.add_item_appointment(self.product, self.following_slot_2)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_booked_adjacent_slots(self.slot))

    def test_is_blocked_by_settings_date(self):
        self.slot.start = timezone.now() + timedelta(days=31)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_settings(self.slot))

    def test_is_not_blocked_by_settings_date(self):
        self.slot.start = timezone.now() + timedelta(days=30)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_settings(self.slot))

    def test_is_blocked_by_settings_days(self):
        self.settings.prevent_bookings_after_days = 20
        self.settings.save()
        self.slot.start = timezone.now() + timedelta(days=21)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_settings(self.slot))

    def test_is_not_blocked_by_settings_days(self):
        self.settings.prevent_bookings_after_days = 20
        self.settings.save()
        self.slot.start = timezone.now() + timedelta(days=20)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_settings(self.slot))


class TestSlotDistantAvailabilityCase(BaseSlotTestCase):

    def setUp(self):
        super().setUp()

        # Tomorrow at noon as datum so the tests are not affected by buffers or slots in the past
        datum = timezone.now() + timedelta(days=1)
        datum = datum.replace(hour=12, minute=0, second=0, microsecond=0)

        self.slot.start = datum
        self.slot.save()
        self.cart = Cart.objects.create()
        self.product = Product.objects.create(name="product")
        self.preceding_slot_1 = Slot.objects.create(
            start=datum - timedelta(hours=1),
            duration=30,
            buffer=30,
            room=self.room1,
        )
        self.following_slot_1 = Slot.objects.create(
            start=datum + timedelta(hours=1),
            duration=30,
            buffer=30,
            room=self.room1,
        )
        self.distant_before_slot_1 = Slot.objects.create(
            start=datum - timedelta(hours=3),
            duration=30,
            buffer=30,
            room=self.room1
        )

        self.distant_after_slot_1 = Slot.objects.create(
            start=self.slot.block_end + timedelta(hours=3),
            duration=30,
            buffer=30,
            room=self.room1
        )

    def test_is_blocked_by_distant_booked_slot(self):
        self.cart.add_item_appointment(self.product, self.distant_before_slot_1)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(True, SlotAvailabilityService.is_blocked_by_booked_distant_slots(self.slot))

    def test_is_not_blocked_by_distant_booked_slot_if_near_slot_also_booked(self):
        self.cart.add_item_appointment(self.product, self.distant_before_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        CartToOrderService.cart_to_order(self.cart)
        self.assertEqual(False, SlotAvailabilityService.is_blocked_by_booked_distant_slots(self.slot))
