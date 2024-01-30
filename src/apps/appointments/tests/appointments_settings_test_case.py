from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from apps.appointments.models.appointments_settings import AppointmentsSettings


class AppointmentsSettingsTestCase(TestCase):

    def setUp(self):
        self.settings = AppointmentsSettings.objects.create(
            prevent_bookings_after_date=timezone.now() + timedelta(days=30),
            prevent_bookings_after_days=90,
            buffer_in_minutes=180,
            parallel_slot_frame_in_minutes=15,
            adjacent_slot_frame_in_minutes=15,
            parallel_incentive_discount=5,
            adjacent_incentive_discount=2,
        )
