from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.appointments.models import Slot, Room
from apps.shop.models import Cart, Product
from .appointments_settings_test_case import AppointmentsSettingsTestCase


class BaseSlotTestCase(AppointmentsSettingsTestCase):
    def setUp(self):
        super().setUp()
        self.room1 = Room.objects.create(name="room 1")
        self.room2 = Room.objects.create(name="room 2")
        self.slot = Slot.objects.create(
            start=timezone.now(),
            duration=30,
            buffer=30,
            room=self.room1,
        )


class TestSaveSlotCase(BaseSlotTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.conflicting_slot = Slot(
            start=timezone.now(),
            duration=30,
            buffer=30,
            room=self.room1,
        )

    def test_slot_save_successful(self):
        self.conflicting_slot.start = timezone.now() - timedelta(minutes=60)
        self.conflicting_slot.save()
        self.slot.save()

    def test_slot_overlap_different_room_save_successful(self):
        self.conflicting_slot.start = timezone.now()
        self.conflicting_slot.room = self.room2
        self.conflicting_slot.save()
        self.slot.save()

    def test_conflicting_slot_crosses_start_save_raises_validation_error(self):
        self.conflicting_slot.start = timezone.now() - timedelta(minutes=25)
        with self.assertRaises(ValidationError):
            self.conflicting_slot.save()

    def test_conflicting_slot_crosses_end_save_raises_validation_error(self):
        self.conflicting_slot.start = timezone.now() + timedelta(minutes=25)
        with self.assertRaises(ValidationError):
            self.conflicting_slot.save()

    def save_conflicting_slot_same_start_and_end_raises_validation_error(self):
        self.conflicting_slot.start = timezone.now()
        with self.assertRaises(ValidationError):
            self.conflicting_slot.save()


class TestDeleteSlotCase(BaseSlotTestCase):

    def test_delete_successful(self):
        self.slot.is_booked = lambda: False
        self.slot.delete()


    def test_delete_booked_slot_raises_validation_error(self):
        self.slot.is_booked = lambda: True
        with self.assertRaises(ValidationError):
            self.slot.delete()


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
        self.assertEqual(True, self.slot.is_reserved())

    def test_is_not_reserved(self):
        self.assertEqual(False, self.slot.is_reserved())

    def test_is_booked(self):
        self.slot.start = timezone.now() + timedelta(days=1)
        self.cart.add_item_appointment(self.product, self.slot)
        self.cart.status = self.cart.Status.COMPLETED
        self.assertEqual(True, self.slot.is_booked())

    def test_is_affected_by_buffer(self):
        self.slot.start = timezone.now() + timedelta(hours=1)
        self.assertEqual(True, self.slot.is_affected_by_buffer())

    def test_is_not_affected_by_buffer(self):
        self.slot.start = timezone.now() + timedelta(hours=3, minutes=1)
        self.assertEqual(False, self.slot.is_affected_by_buffer())

    def test_preceding_booked_slot_negates_buffer_effect(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.set_completed()
        self.assertEqual(False, self.slot.is_affected_by_buffer())

    def test_parallel_booked_slot_negates_buffer_effect(self):
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        self.cart.set_completed()
        self.assertEqual(False, self.slot.is_affected_by_buffer())

    def test_is_blocked_by_booked_slots_two_preceding_one_parallel(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_2)
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        self.cart.set_completed()
        self.assertEqual(True, self.slot.is_blocked_by_booked_slots())

    def test_is_blocked_by_booked_slots_two_following_one_parallel(self):
        self.cart.add_item_appointment(self.product, self.following_slot_1)
        self.cart.add_item_appointment(self.product, self.following_slot_2)
        self.cart.add_item_appointment(self.product, self.parallel_slot)
        self.cart.set_completed()
        self.assertEqual(True, self.slot.is_blocked_by_booked_slots())

    def test_is_not_blocked_by_booked_slots_two_preceding_two_following(self):
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_2)
        self.cart.add_item_appointment(self.product, self.following_slot_1)
        self.cart.add_item_appointment(self.product, self.following_slot_2)
        self.cart.set_completed()
        self.assertEqual(False, self.slot.is_blocked_by_booked_slots())

    def test_is_blocked_by_settings_date(self):
        self.slot.start = timezone.now() + timedelta(days=31)
        self.assertEqual(True, self.slot.is_blocked_by_settings())

    def test_is_not_blocked_by_settings_date(self):
        self.slot.start = timezone.now() + timedelta(days=30)
        self.assertEqual(False, self.slot.is_blocked_by_settings())

    def test_is_blocked_by_settings_days(self):
        self.settings.prevent_bookings_after_days = 20
        self.settings.save()
        self.slot.start = timezone.now() + timedelta(days=21)
        self.assertEqual(True, self.slot.is_blocked_by_settings())

    def test_is_not_blocked_by_settings_days(self):
        self.settings.prevent_bookings_after_days = 20
        self.settings.save()
        self.slot.start = timezone.now() + timedelta(days=20)
        self.assertEqual(False, self.slot.is_blocked_by_settings())

class TestSlotDistantAvailabilityCase(BaseSlotTestCase):

    def setUp(self):
        super().setUp()
        datum = timezone.datetime(timezone.now().year, timezone.now().month, timezone.now().day + 1, 12, 0, 0)
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
        self.cart.set_completed()
        self.assertEqual(True, self.slot.is_blocked_by_booked_distant_slots())

    def test_is_not_blocked_by_distant_booked_slot_if_near_slot_also_booked(self):
        self.cart.add_item_appointment(self.product, self.distant_before_slot_1)
        self.cart.add_item_appointment(self.product, self.preceding_slot_1)
        self.cart.set_completed()
        self.assertEqual(False, self.slot.is_blocked_by_booked_distant_slots())

