from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType

from ..models import (
    Cart,
    CartCoupon,
    CartItemAppointment,
    CartItemCoupon,
    Product,
    ProductGroupCoupon,
    ProductGroupAppointment
)


class CartItemAppointmentInlineForm(forms.ModelForm):

    class Meta:
        model = CartItemAppointment
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(ProductGroupAppointment)
        self.fields['product'].queryset = Product.objects.filter(
            product_group__real_type=content_type,
        )


class CartItemCouponInlineForm(forms.ModelForm):

    class Meta:
        model = CartItemCoupon
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(ProductGroupCoupon)
        self.fields['product'].queryset = Product.objects.filter(
            product_group__real_type=content_type,
        )


class TabularInlineCartItemAppointments(admin.TabularInline):
    model = CartItemAppointment
    form = CartItemAppointmentInlineForm


class TabularInlineCartItemCoupons(admin.TabularInline):
    model = CartItemCoupon
    form = CartItemCouponInlineForm


class TabularInlineCartCoupons(admin.TabularInline):
    model = CartCoupon


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'status',
    ]
    inlines = [
        TabularInlineCartItemAppointments,
        TabularInlineCartItemCoupons,
        TabularInlineCartCoupons,
    ]

