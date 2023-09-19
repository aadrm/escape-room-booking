from django.contrib import admin

from ..models import CartItemAppointment


@admin.register(CartItemAppointment)
class CartItemAppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'pk'
    ]
