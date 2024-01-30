import logging

from datetime import timedelta
from django.db.models.query import QuerySet
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class Slot(models.Model):

    class Availability(models.IntegerChoices):
        DEFAULT = 1, 'Default'
        DISABLED = 2, 'Disabled'
        IGNORE_BLOCKED_ADJACENT = 3, 'Ignore blocked by adjacent'

    start = models.DateTimeField(_('Start'), auto_now=False, auto_now_add=False)
    duration = models.PositiveSmallIntegerField(_('Duration'), default=60)
    buffer = models.PositiveSmallIntegerField(_('Buffer'), default=30)
    availability = models.PositiveBigIntegerField('availability', choices=Availability.choices, default=Availability.DEFAULT)
    appointment_end = models.DateTimeField(editable=False, blank=True, null=True)
    block_end = models.DateTimeField(editable=False, blank=True, null=True)

    room = models.ForeignKey(
        'appointments.Room',
        verbose_name=_('Room'),
        on_delete=models.CASCADE
    )
    schedule = models.ForeignKey(
        'appointments.Schedule',
        verbose_name=_('Schedule'),
        related_name=_('slots'),
        related_query_name=_('slots'),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def _overlapping_slots(self) -> QuerySet:
        overlapping_slots = Slot.objects.filter(
            start__lt=self.block_end,
            block_end__gt=self.start,
        ).exclude(
            pk=self.pk
        )
        return overlapping_slots

    def _overlapping_same_room_slots(self):
        return self._overlapping_slots().filter(room=self.room)

    def disable(self) -> None:
        self.availability = self.Availability.DISABLED

    def enable(self) -> None:
        self.availability = self.Availability.DEFAULT

    def keep_open(self) -> None:
        self.availability = self.Availability.IGNORE_BLOCKED_ADJACENT

    @property
    def is_enabled(self) -> bool:
        return (
            self.availability == self.Availability.DEFAULT or
            self.availability == self.Availability.IGNORE_BLOCKED_ADJACENT
        )

    def is_booked(self) -> bool:
        # imported here to avoid circular import, not ideal
        from ..services.slot_availability_service import SlotAvailabilityService
        return SlotAvailabilityService.is_booked(self)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return str(self.room) + ' | ' + self.start.astimezone().strftime('%Y-%m-%d %H:%M')

    def raise_validation_error_if_deleting_booked_slot(self):
        if self.is_booked():
            raise ValidationError(f'Cannot delete booked slot: {str(self)}')
    def raise_validation_error_if_conflicts_with_another_slot(self):
        conflicting_slots = self._overlapping_same_room_slots()
        if conflicting_slots.exists():
            raise ValidationError("Slot overlaps with other slots")

    def save(self, *args, **kwargs):
        # Trim seconds and milliseconds
        # This way microsecond overlaps are prevented, important during testing
        self.start = self.start.replace(second=0, microsecond=0)

        # set derived attributes
        self.appointment_end = self.start + timedelta(minutes=self.duration)
        self.block_end = self.start + timedelta(minutes=self.duration + self.buffer)

        try:
            self.raise_validation_error_if_conflicts_with_another_slot()
            super().save(*args, **kwargs)
        except ValidationError as error:
            logger.warning(error)

    def delete(self, *args, **kwargs):
        try:
            self.raise_validation_error_if_deleting_booked_slot()
            super().delete(*args, **kwargs)
        except ValidationError as error:
            logger.warning(error)

