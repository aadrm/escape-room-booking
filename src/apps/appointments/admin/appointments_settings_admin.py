from django.contrib import admin

from .. import models


@admin.register(models.AppointmentsSettings)
class AppointmentsSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'edit',
        'prevent_bookings_after_date',
        'prevent_bookings_after_days',
        'buffer_in_minutes',
    ]
    """Admin
    """

    def edit(self, obj):
        return 'Change settings'

    def get_actions(self, request):
        return []
