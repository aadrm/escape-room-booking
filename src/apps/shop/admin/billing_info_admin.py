from django.contrib import admin

from ..models import (
    BillingInfo,
)


@admin.register(BillingInfo)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'phone_number',
    ]
    search_fields = [
        'name',
        'email',
    ]

