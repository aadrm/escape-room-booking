import ast

from django.db import models
from django.utils.translation import gettext_lazy as _
from .slot import Slot

class Schedule(models.Model):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAY_CHOICES = [
        (MONDAY, _('Mon')),
        (TUESDAY, _('Tue')),
        (WEDNESDAY, _('Wed')),
        (THURSDAY, _('Thu')),
        (FRIDAY, _('Fri')),
        (SATURDAY, _('Sat')),
        (SUNDAY, _('Sun')),
    ]
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

    def _delete_related_not_booked_slots(self):
        slots = self.get_slots()
        for slot in slots:
            if not slot.is_booked():
                slot.delete()


    def set_days_of_week(self, days):
        self.days_of_week = ','.join(str(day) for day in days)

    def get_days_of_week(self):
        return [int(day) for day in ast.literal_eval(self.days_of_week) if day]

    def get_days_of_week_display(self):
        days = self.get_days_of_week()
        print(days)
        return [dict(self.DAY_CHOICES)[day] for day in days]

    def save(self, *args, **kwargs):
        self._delete_related_not_booked_slots()
        super().save(*args, **kwargs)
        Slot.create_slots_bound_to_schedule(
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
