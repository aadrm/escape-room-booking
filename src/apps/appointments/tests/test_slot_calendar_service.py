from datetime import time

from django.utils import timezone
from django.utils.timezone import timedelta

from apps.appointments.models import Slot, Room, Schedule
from apps.appointments.services import SlotCalendarService
from . import AppointmentsSettingsTestCase

class SlotCalendarServiceTestCase(AppointmentsSettingsTestCase):

    def setUp(self):
        current_date = timezone.now().date()
        first_day_next_month = current_date.replace(month=current_date.month + 1, day=1)
        self.room = Room.objects.create(name="Room1")
        Schedule.objects.create(
            start_date=first_day_next_month,
            end_date=first_day_next_month + timedelta(days=15),
            start_time=time(12, 0),
            days_of_week='[0, 1]',
            duration_minutes=30,
            buffer_minutes=30,
            repeat_times=4,
            room=self.room,
        )

    def test_slot_days(self):
        SlotCalendarService.days_with_free_slots_in_month_by_room(year=2024, month=2, room=self.room)
        return True
