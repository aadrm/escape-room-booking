from django.contrib import admin

from ..models import CartProductAppointment


@admin.register(CartProductAppointment)
class CartProductAppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'pk'
    ]
