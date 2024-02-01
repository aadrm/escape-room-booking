from django.contrib import admin
from django import forms

from common.days_of_week_form_mixin import DaysOfWeekFormMixin
from ..models import Coupon


class CustomCouponForm(DaysOfWeekFormMixin, forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'reference',
        'code',
    ]
    form = CustomCouponForm

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['days_of_week'] = [0, 1, 2, 3, 4, 5, 6]
        return initial
