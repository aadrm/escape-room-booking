from django.contrib import admin
from django.db import models
from django import forms

from django.utils.translation import gettext_lazy as _

from ..models import Schedule

class CustomScheduleForm(forms.ModelForm):
    # Customizations to the form fields or behavior can be added here
    DAY_CHOICES = Schedule.DAY_CHOICES
    days_of_week = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super(CustomScheduleForm, self).__init__(*args, **kwargs)
        if self.instance:

        # assign a (computed, I assume) default value to the choice field
            self.initial['days_of_week'] = self.instance.get_days_of_week()

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


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            form.initial = {'days_of_week': [0, 2]}
        return form

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['days_of_week'] = [0, 1]  # Set the initial value here
        return initial

    def start_24h(self, obj):
        return obj.start_time.strftime('%H:%M')
    start_24h.short_description = "start"