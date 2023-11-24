from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import AppointmentsSettings


class Slot(models.Model):
    """A bookable slot in the calendar
    """
    start = models.DateTimeField(_("Start"), auto_now=False, auto_now_add=False)
    duration = models.PositiveSmallIntegerField(_("Duration"), default=60)
    buffer = models.PositiveSmallIntegerField(_("Buffer"), default=30)
    is_enabled = models.BooleanField(_("Enabled"), default=True)
    appointment_end = models.DateTimeField(editable=False, blank=True, null=True)
    block_end = models.DateTimeField(editable=False, blank=True, null=True)

    room = models.ForeignKey(
        "appointments.Room",
        verbose_name=_("Room"),
        on_delete=models.CASCADE
    )
    schedule = models.ForeignKey(
        "appointments.Schedule",
        verbose_name=_("Schedule"),
        related_name=_("slots"),
        related_query_name=_("slots"),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def is_available(self):
        return  self.is_available_to_staff() \
            and not self.is_affected_by_buffer() \
            and not self.is_enabled\

    def is_available_to_staff(self):
        return not self.is_reserved() \
            and self._is_start_in_future()

    def is_reserved(self):
        related_cart_items = self.cartitemappointment_set.all()
        for item in related_cart_items:
            if item.cart.is_slot_blocking():
                return True

    def __str__(self):
        return str(self.room) + ' | ' +  self.start.astimezone().strftime("%Y-%m-%d %H:%M" )

    def _is_start_in_future(self):
        return self.start > timezone.now()

    def _get_other_slots_end_after_start_before(self, after_datetime, before_datetime):
        return Slot.objects.filter(block_end__gte=after_datetime, start__lte=before_datetime).exclude(pk=self.pk)

    def _get_other_slots_by_start_between_datetimes(self, after_datetime, before_datetime):
        """ Uses the start of sessions as reference
        """
        return Slot.objects.filter(start__gte=after_datetime, start__lte=before_datetime).exclude(pk=self.pk)

    def is_booked(self):
        # for item in self.cart_items.all():
        #     if item.status > 0:
        return self.is_enabled

    def is_affected_by_buffer(self):
         return not self.is_future_of_buffer() and not self.is_adjacent_after_to_taken_slot()

    def is_future_of_buffer(self):
         this_moment = timezone.now()
         buffer = this_moment + timedelta(minutes=AppointmentsSettings.load().buffer_in_minutes)
         return self.start > buffer

    def is_adjacent_after_to_taken_slot(self):
        slots = self.get_before_after_minutes_slots(20, 110)
        for slot in slots:
            if slot.is_booked():
                return True
        return False

    def get_adjacent_slots(self):
        minutes = AppointmentsSettings.load().adjacent_slot_frame_in_minutes
        after_datetime = self.start - timedelta(minutes=minutes)
        before_datetime = self.block_end + timedelta(minutes=minutes)
        return self._get_other_slots_end_after_start_before(self, after_datetime, before_datetime)

    def get_parallel_slots(self):
        minutes = AppointmentsSettings.load().parallel_slot_frame_in_minutes
        after_datetime = self.start - timedelta(minutes=minutes)
        before_datetime = self.start + timedelta(minutes=minutes)
        return self._get_other_slots_by_start_between_datetimes(self, after_datetime, before_datetime)

    def is_parallel_to_taken_slot(self):
        for slot in parallel_slots:
            if slot.is_booked():
                return True
        return False

    def _overlapping_slots(self):
        overlapping_slots = Slot.objects.filter(
            start__lt=self.block_end,
            block_end__gt=self.start,
        ).exclude(
            pk=self.pk
        )
        return overlapping_slots

    def _overlapping_same_room_slots(self):
        return self._overlapping_slots().filter(room=self.room)

    @classmethod
    def create_slots_bound_to_schedule(
            cls,
            *,
            schedule,
            start_date,
            end_date,
            days_of_week,
            start_time,
            duration_minutes,
            buffer_minutes,
            room,
            repeat_times,
        ):
        # slots = []
        current_date = max(start_date, timezone.now().date())
        while current_date <= end_date:
            current_datetime = timezone.datetime.combine(current_date, start_time)
            if current_datetime.weekday() in days_of_week:
                for n in range(repeat_times):
                    slot = cls(
                        start=current_datetime,
                        duration=duration_minutes,
                        buffer=buffer_minutes,
                        room=room,
                        schedule=schedule,
                    )
                    current_datetime += timedelta(minutes=duration_minutes + buffer_minutes)
                    try:
                        slot.save()
                    except ValidationError as e:
                        print(e)
            current_date += timedelta(days=1)

    class Meta:
        ordering = ['room', 'start']

    def save(self, *args, **kwargs):
        self.appointment_end = self.start + timedelta(minutes=self.duration)
        self.block_end = self.start + timedelta(minutes=self.duration + self.buffer)
        conflicting_slots = self._overlapping_same_room_slots()
        if conflicting_slots.exists():
            raise ValidationError("Slot overlaps with other slots")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_booked():
            # Slot is booked, prevent deletion
            raise ValidationError("Cannot delete a booked slot.")
        super().delete(*args, **kwargs)