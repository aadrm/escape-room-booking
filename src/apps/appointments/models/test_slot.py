from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.appointments.models import Slot, Room


class BaseSlotTestCase(TestCase):

    def setUp(self):
        self.room1 = Room.objects.create(name="room 1")
        self.room2 = Room.objects.create(name="room 2")
        self.slot = Slot.objects.create(
            start=datetime(2023, 7, 10, 12, 30),
            duration=30,
            buffer=30,
            room=self.room1,
        )


class TestSaveSlotCase(BaseSlotTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.conflicting_slot = Slot(
            start=datetime(2023, 7, 10, 11, 30),
            duration=30,
            buffer=30,
            room=self.room1,
        )


    def test_slot_save_successful(self):
        self.conflicting_slot.start = datetime(2023, 7, 10, 11, 30)
        self.conflicting_slot.save()
        self.slot.save()

    def test_slot_overlap_different_room_save_successful(self):
        self.conflicting_slot.start = datetime(2023, 7, 10, 12, 30)
        self.conflicting_slot.room = self.room2
        self.conflicting_slot.save()
        self.slot.save()

    def test_conflicting_slot_crosses_start_save_raises_validation_error(self):
        self.conflicting_slot.start = datetime(2023, 7, 10, 11, 31)
        with self.assertRaises(ValidationError):
            self.conflicting_slot.save()

    def test_conflicting_slot_crosses_end_save_raises_validation_error(self):
        self.conflicting_slot.start = datetime(2023, 7, 10, 13, 29)
        with self.assertRaises(ValidationError):
            self.conflicting_slot.save()

    def save_conflicting_slot_same_start_and_end_raises_validation_error(self):
        self.conflicting_slot.start = datetime(2023, 7, 10, 12, 30)
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

