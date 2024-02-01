# from typing import Optional
from django.contrib import admin
# from django.http.request import HttpRequest

from .. import models


@admin.register(models.ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'edit',
        'default_coupon_validity_in_days',
        'default_coupon_code_length'
    ]

    def edit(self, obj):
        return 'Change settings'

    def get_actions(self, request):
        return []
