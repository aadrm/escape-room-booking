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
        verbose_name=()
    )

    adjacent_slot_frame_in_minutes = models.PositiveSmallIntegerField(
        verbose_name=()
    )



