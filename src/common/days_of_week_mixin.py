import ast

from django.utils.translation import gettext_lazy as _

from .day_choices import DAY_CHOICES


class DaysOfWeekMixin:

    DAY_CHOICES = DAY_CHOICES

    def set_days_of_week(self, days):
        self.days_of_week = ','.join(str(day) for day in days)

    def get_days_of_week(self):
        return [int(day) for day in ast.literal_eval(self.days_of_week)]

    def get_days_of_week_display(self):
        days = self.get_days_of_week()
        return [dict(self.DAY_CHOICES)[day] for day in days]
