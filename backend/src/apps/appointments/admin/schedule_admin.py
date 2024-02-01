from django.contrib import admin
from django.db import models
from django import forms

from django.utils.translation import gettext_lazy as _

from common.days_of_week_form_mixin import DaysOfWeekFormMixin
from ..models import Schedule


class CustomScheduleForm(DaysOfWeekFormMixin, forms.ModelForm):
    # # Customizations to the form fields or behavior can be added here
    class Meta:
        model = Schedule
        fields = '__all__'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'room',
        'display_days_of_week',
        'start_date',
        'end_date',
        'start_24h',
        'repeat_times',
    ]
    list_filter = ['days_of_week']
    form = CustomScheduleForm
    formfield_overrides = {
        models.CharField: {'widget': forms.CheckboxSelectMultiple},
    }

    def display_days_of_week(self, obj):
        selected_days = obj.get_days_of_week_display()
        return selected_days
    display_days_of_week.short_description = _('Days of Week')

    def start_24h(self, obj):
        return obj.start_time.strftime('%H:%M')
    start_24h.short_description = "start"
