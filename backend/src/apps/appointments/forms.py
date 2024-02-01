from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Room


class SlotCreationForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    days_of_week = forms.MultipleChoiceField(choices=[
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ], widget=forms.CheckboxSelectMultiple)
    start_time = forms.TimeField()
    duration_minutes = forms.IntegerField()
    buffer_minutes = forms.IntegerField()
    # room = forms.ModelChoiceField(Room)