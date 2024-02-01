from django.contrib import admin
from django.utils.html import format_html
from django import forms

from ..models import (
    Order,
    OrderItem
)


class OrderItemInlineForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        exclude = []


class TabularInlineOrderItem(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'cart_link',
        'billing_info_str',
        'order_placed',
        'base_total',
        'gross_total',
    ]
    date_hierarchy = 'order_placed'
    readonly_fields = [
        'order_number',
        'order_placed',
        'last_modified',
        'base_total',
        'gross_total',
        'net_total',
        'vat_total',
    ]
    inlines = [
        TabularInlineOrderItem,
    ]

    def cart_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.cart.get_absolute_url(), obj.cart)

    cart_link.short_description = "Cart"