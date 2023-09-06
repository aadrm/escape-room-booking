from django import forms
from .day_choices import DAY_CHOICES


class DaysOfWeekFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_days_of_week_field()
        self.initialize_days_of_week_initial()

    def setup_days_of_week_field(self):
        self.fields['days_of_week'] = forms.MultipleChoiceField(
            choices=DAY_CHOICES,
            widget=forms.CheckboxSelectMultiple,
        )

    def initialize_days_of_week_initial(self):
        if self.instance.pk:
            self.initial['days_of_week'] = self.instance.get_days_of_week()
