from django.utils import timezone

from django.test import TestCase
from apps.appointments.models import Slot, Room


class BaseScheduleTestCase(TestCase):

    def setUp(self):
        self.room1 = Room.objects.create(name='room1')
