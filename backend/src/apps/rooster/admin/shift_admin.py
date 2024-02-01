from django.contrib import admin

from ..models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """ Shift Admin
    """