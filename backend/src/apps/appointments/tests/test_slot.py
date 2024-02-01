from django.utils import timezone
from django.utils.timezone import timedelta
from apps.appointments.models import Slot, Room
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

    def test_conflicting_slot_crosses_start_not_saved(self):
        self.conflicting_slot.start = timezone.now() - timedelta(minutes=25)
        self.conflicting_slot.save()
        saved_slots = Slot.objects.filter(id=self.conflicting_slot.id)
        self.assertQuerysetEqual(saved_slots, [])

    def test_conflicting_slot_crosses_end_not_saved(self):
        self.conflicting_slot.start = timezone.now() + timedelta(minutes=25)
        self.conflicting_slot.save()
        saved_slots = Slot.objects.filter(id=self.conflicting_slot.id)
        self.assertQuerysetEqual(saved_slots, [])

    def save_conflicting_slot_same_start_and_end_not_saved(self):
        self.conflicting_slot.start = timezone.now()
        self.conflicting_slot.save()
        saved_slots = Slot.objects.filter(id=self.conflicting_slot.id)
        self.assertQuerysetEqual(saved_slots, [])


class TestDeleteSlotCase(BaseSlotTestCase):

    def test_delete_successful(self):
        # Mock is_booked method to return False
        self.slot.is_booked = lambda: False

        # Delete the slot
        self.slot.delete()

        # Check that the slot does not exist in the database
        deleted_slots = Slot.objects.filter(id=self.slot.id)
        self.assertQuerysetEqual(deleted_slots, [])

    def test_delete_booked_slot_not_deleted(self):
        self.slot.is_booked = lambda: True
        self.slot.delete()
        self.assertTrue(self.slot)





