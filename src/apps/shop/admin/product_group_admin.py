from django.contrib import admin
from ..models import ProductGroupCoupon, ProductGroupAppointment


class ProductGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


admin.site.register(ProductGroupCoupon, ProductGroupAdmin)
admin.site.register(ProductGroupAppointment, ProductGroupAdmin)
