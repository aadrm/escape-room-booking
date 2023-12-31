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


