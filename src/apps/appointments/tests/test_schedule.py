from datetime import time
from django.utils import timezone
from django.utils.timezone import timedelta

from django.test import TestCase
from apps.appointments.models import Room, Schedule


class BaseScheduleTestCase(TestCase):

    def setUp(self):
        self.room1 = Room.objects.create(name='room1')
        self.schedule = Schedule.objects.create(
            start_date=timezone.datetime.now().date(),
            end_date=timezone.datetime.now().date() + timedelta(days=6),
            days_of_week="['0', '1']",
            start_time=time(hour=12),
            repeat_times=2,
            room=self.room1,
        )



class TestScheduleSlotInteraction(BaseScheduleTestCase):

    def test_create_slots(self):
        self.assertEqual(4, self.schedule.get_slots().count())


