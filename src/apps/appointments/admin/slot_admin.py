from typing import Any
from django.contrib import admin, messages
from django.contrib.messages.storage import default_storage
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest

from ..models import Slot


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    actions = [
        'enable_slots',
        'disable_slots',
        'print_to_console',
        ]
    date_hierarchy = 'start'
    list_display = [
        'start_24h',
        'room',
        'is_enabled'
    ]
    list_filter = ['room', 'start']

    def enable_slots(self, request, queryset):
        queryset.update(is_enabled=True)

    enable_slots.short_description = "Enable selected slots"

    def disable_slots(self, request, queryset):
        queryset.update(is_enabled=False)

    disable_slots.short_description = "Disable selected slots"

    def print_to_console(self, request, queryset):
        print('Action execute')

    def start_24h(self, obj):
        return obj.start.strftime('%Y-%b-%d %H:%M')
    start_24h.short_description="start"

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        try:
            super().save_model(request, obj, form, change)
            # obj.save()
        except ValidationError as e:
            self.message_user(request, e, level=messages.WARNING)


    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        try:
            super().delete_model(request, obj)
        except ValidationError as e:
            self.message_user(request, e, level=messages.WARNING)
