import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from apps.rooster.models import Shift

# Create your tests here.

class BaseShiftTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="user1", password="testing321")
        self.user2 = User.objects.create(username="user2", password="testing321")
        self.shift1 = Shift(
            employee=self.user1,
            shift_date=datetime.date.today()
        )
        self.shift2 = Shift(
            employee=self.user2,
            shift_date=datetime.date.today()
        )


class TestSaveShiftCase(BaseShiftTestCase):

    def test_shift_save_successful(self):
        self.shift1.save()

    def test_shift_not_save_when_shift_wih_same_date_exists(self):
        self.shift1.save()
        with self.assertRaises(ValidationError):
            self.shift2.save()