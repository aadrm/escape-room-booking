from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from common.singleton import SingletonModel


def default_prevent_bookings_after_date():
    return timezone.now() + timedelta(days=90)


class AppointmentsSettings(SingletonModel):
    """ Allows to set global settings using the admin interface
    """
    prevent_bookings_after_date = models.DateField(
        verbose_name=_('Prevent bookings after date'),
        default=default_prevent_bookings_after_date
    )
    prevent_bookings_after_days = models.PositiveSmallIntegerField(
        verbose_name=_('Prevent bookings after days'),
        default=90,
    )
    buffer_in_minutes = models.PositiveSmallIntegerField(
        verbose_name=_('Buffer in minutes'),
        default=180,
    )

    parallel_slot_frame_in_minutes = models.PositiveSmallIntegerField(
        verbose_name=_("Consider parallel other slots that start within this number of minutes from each other"),
        default=15,
    )

    adjacent_slot_frame_in_minutes = models.PositiveSmallIntegerField(
        verbose_name=("Consider adjacent other slots that end within this amount of minutes from the start of each other"),
        default=15,
    )

    booked_adjacent_slots_blocking_count = models.PositiveSmallIntegerField(
        verbose_name=("This many booked preceding or following slots will affect the availability of other slots"),
        default=2,
    )

    booked_parallel_slots_blocking_count = models.PositiveSmallIntegerField(
        verbose_name=("This amount of booked parallel slots will affect the availability of other slots"),
        default=1,
    )

    booked_distant_slots_block_minutes = models.PositiveSmallIntegerField(
        verbose_name=("Block slots this many minutes away from other slots on the same day"),
        default=90,
    )

    parallel_incentive_discount = models.DecimalField(
        verbose_name=("Parallel incentive discount in euro"),
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    adjacent_incentive_discount = models.DecimalField(
        verbose_name=("Parallel incentive discount in euro"),
        max_digits=3,
        decimal_places=2,
        default=0,
    )


    def get_earliest_slot_date_limit(self):
        date_limit = AppointmentsSettings.load().prevent_bookings_after_date
        day_limit = AppointmentsSettings.load().prevent_bookings_after_days
        day_limit_date = timezone.now().date() + timedelta(days=day_limit)
        return min(date_limit, day_limit_date)


    class Meta:
        verbose_name_plural = " Settings"  # The space is a hack so this model admin occupies the first place




