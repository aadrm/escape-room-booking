from datetime import datetime, timedelta
from django.db.models.query import QuerySet
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import AppointmentsSettings


class Slot(models.Model):
    """A bookable slot in the calendar

    Slots can be in one of several states which are a combination of different conditions
    + available (if not unavailable, bookable through the booking calendar)
    + unavailable (not available in the booking calendar)
        - booked (in a cart where the order has been completed)
        - not in the future
        + bookable by staff (A staff member could assign a slot to a booking)
            - blocked (Blocked due to a combination of conditions)
                - not enabled
                - affected by buffer (within the buffer time and no adjacent-before slots)
                - affected by settings (prevent after date/days)
                - blocked by other bookings (smart calendar)
            - reserved (in an "open" order and reserved for some time)
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

    def is_available(self) -> bool:
        return self.is_available_to_staff() \
            and not self.is_affected_by_buffer() \
            and not self.is_blocked_by_booked_slots() \
            and not self.is_enabled\

    def is_available_to_staff(self) -> bool:
        return not self.is_reserved() \
            and self._is_start_in_future()

    def is_reserved(self) -> bool:
        return hasattr(self, 'cart_item_appointment') \
            and self.cart_item_appointment.is_reserving_slot()

    def is_booked(self) -> bool:
        return hasattr(self, 'cart_item_appointment') \
            and self.cart_item_appointment.is_booking_slot()

    def get_preceding_slots(self) -> QuerySet:
        minutes = AppointmentsSettings.load().adjacent_slot_frame_in_minutes
        after_datetime = self.start - timedelta(minutes=minutes)
        before_datetime = self.start + timedelta(minutes=minutes)
        return self._get_slots_by_block_end_between_datetimes(after_datetime, before_datetime)

    def get_following_slots(self) -> QuerySet:
        minutes = AppointmentsSettings.load().adjacent_slot_frame_in_minutes
        after_datetime = self.block_end - timedelta(minutes=minutes)
        before_datetime = self.block_end + timedelta(minutes=minutes)
        return self._get_slots_by_start_between_datetimes(after_datetime, before_datetime)

    def get_parallel_slots(self) -> QuerySet:
        minutes = AppointmentsSettings.load().parallel_slot_frame_in_minutes
        after_datetime = self.start - timedelta(minutes=minutes)
        before_datetime = self.start + timedelta(minutes=minutes)
        return self._get_slots_by_start_between_datetimes(after_datetime, before_datetime)

    def get_same_date_slots(self) -> QuerySet:
        slot_date = self.start.date()
        return Slot.objects.filter(start__date=slot_date)

    def get_near_slots(self) -> QuerySet:
        minutes = AppointmentsSettings.load().booked_distant_slots_block_minutes
        after_datetime = self.start - timedelta(minutes=minutes)
        before_datetime = self.block_end + timedelta(minutes=minutes)
        return Slot.objects.filter(block_end__gte=after_datetime, start__lte=before_datetime)

    def get_distant_slots(self) -> QuerySet:
        near_slots = self.get_near_slots()
        day_slots = self.get_same_date_slots()
        return day_slots.exclude(pk__in=near_slots.values('pk'))

    def is_preceding_slot_booked(self) -> bool:
        slots = self.get_preceding_slots()
        return self.is_at_least_one_slot_taken(slots)

    def is_parallel_slot_booked(self) -> bool:
        slots = self.get_parallel_slots()
        return self.is_at_least_one_slot_taken(slots)

    def is_affected_by_buffer(self) -> bool:
        return not self.is_future_of_buffer() and \
            not self.is_preceding_slot_booked() and \
            not self.is_parallel_slot_booked()

    def is_parallel_booked_slot_count_blocking(self) -> bool:
        parallel_block_count = AppointmentsSettings.load().booked_parallel_slots_blocking_count
        return self.taken_slots_count(self.get_parallel_slots()) >= parallel_block_count

    def is_adjacent_booked_slot_count_blocking(self) -> bool:
        adjacent_block_count = AppointmentsSettings.load().booked_adjacent_slots_blocking_count
        return self.taken_slots_count(self.get_preceding_slots()) >= adjacent_block_count or \
            self.taken_slots_count(self.get_following_slots()) >= adjacent_block_count

    def is_blocked_by_booked_slots(self) -> bool:
        return self.is_parallel_booked_slot_count_blocking() and self.is_adjacent_booked_slot_count_blocking()

    def is_distant_slot_booked(self) -> bool:
        distant_slots = self.get_distant_slots()
        return self.is_at_least_one_slot_taken(distant_slots)

    def is_near_slot_booked(self) -> bool:
        near_slots = self.get_near_slots()
        return self.is_at_least_one_slot_taken(near_slots)

    def is_blocked_by_booked_distant_slots(self) -> bool:
        return self.is_distant_slot_booked() and not self.is_near_slot_booked()

    def is_blocked_by_settings(self) -> bool:
        return self.start.date() > AppointmentsSettings.load().get_earliest_slot_date_limit()

    def _is_start_in_future(self) -> bool:
        return self.start >= timezone.now().replace(second=0, microsecond=0)

    def _get_slots_by_block_end_between_datetimes(self, after: datetime, before: datetime) -> QuerySet:
        return Slot.objects.filter(block_end__gte=after, block_end__lte=before)

    def _get_slots_by_start_between_datetimes(self, after: datetime, before: datetime) -> QuerySet:
        return Slot.objects.filter(start__gte=after, start__lte=before).exclude(pk=self.pk)

    def is_future_of_buffer(self) -> bool:
        this_moment = timezone.now()
        buffer = this_moment + timedelta(minutes=AppointmentsSettings.load().buffer_in_minutes)
        return self.start > buffer

    def taken_slots_count(self, slot_queryset: QuerySet) -> int:
        count = 0
        for slot in slot_queryset:
            if slot.is_booked():
                count += 1
        return count

    def is_at_least_one_slot_taken(self, slot_queryset: QuerySet) -> int:
        for slot in slot_queryset:
            if slot.is_booked():
                return True
        return False

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
        self.is_enabled = FALSE

    def enable(self) -> None:
        self.is_enabled = True

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
        ordering = ['start']

    def __str__(self):
        return str(self.room) + ' | ' + self.start.astimezone().strftime("%Y-%m-%d %H:%M")

    def save(self, *args, **kwargs):
        # Trim seconds and milliseconds
        # This way microsecond overlaps are prevented, important during testing
        self.start = self.start.replace(second=0, microsecond=0)

        # set derived attributes
        self.appointment_end = self.start + timedelta(minutes=self.duration)
        self.block_end = self.start + timedelta(minutes=self.duration + self.buffer)

        # check for conflicts
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