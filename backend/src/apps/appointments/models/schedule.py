from django.db import models
from django.utils.translation import gettext_lazy as _
from ..services import SlotFactoryService, SlotAvailabilityService
from common.days_of_week_mixin import DaysOfWeekMixin


class Schedule(models.Model, DaysOfWeekMixin):

    start_date = models.DateField()
    end_date = models.DateField()
    days_of_week = models.CharField(
        max_length=50,
    )
    start_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(
        default=60
    )
    buffer_minutes = models.PositiveSmallIntegerField(
        default=30
    )
    repeat_times = models.IntegerField(
        _("Repeat times"),
        default=1,
        help_text=_("The number of slots to be created each day"))
    room = models.ForeignKey(
        "appointments.Room",
        verbose_name=_("Room"),
        on_delete=models.CASCADE
    )

    def get_slots(self):
        return self.slots.all()

    def _delete_related_free_slots(self):
        slots = self.get_slots()
        for slot in slots:
            if SlotAvailabilityService.is_free(slot):
                slot.delete()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self._delete_related_free_slots()
        super().save(*args, **kwargs)
        SlotFactoryService.create_slots_bound_to_schedule(
            schedule=self,
            start_date=self.start_date,
            end_date=self.end_date,
            days_of_week=self.get_days_of_week(),
            start_time=self.start_time,
            duration_minutes=self.duration_minutes,
            buffer_minutes=self.buffer_minutes,
            room=self.room,
            repeat_times=self.repeat_times,
        )

    def delete(self, *args, **kwargs):
        self._delete_related_free_slots()
        super().delete(*args, **kwargs)
