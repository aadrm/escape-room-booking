from django.contrib import admin
from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ..models import (
    Cart,
    CartCoupon,
    CartProductAppointment,
    CartProductCoupon,
    Product,
    ProductGroupCoupon,
    ProductGroupAppointment
)


class CartProductAppointmentInlineForm(forms.ModelForm):

    class Meta:
        model = CartProductAppointment
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(ProductGroupAppointment)
        self.fields['product'].queryset = Product.objects.filter(
            product_group__real_type=content_type,
        )


class CartProductCouponInlineForm(forms.ModelForm):

    class Meta:
        model = CartProductCoupon
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(ProductGroupCoupon)
        self.fields['product'].queryset = Product.objects.filter(
            product_group__real_type=content_type,
        )


class TabularInlineCartProductAppointments(admin.TabularInline):
    model = CartProductAppointment
    form = CartProductAppointmentInlineForm

class TabularInlineCartProductCoupons(admin.TabularInline):
    model = CartProductCoupon
    form = CartProductCouponInlineForm


class TabularInlineCartCoupons(admin.TabularInline):
    model = CartCoupon


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'status',
    ]
    inlines = [
        TabularInlineCartProductAppointments,
        TabularInlineCartProductCoupons,
        TabularInlineCartCoupons,
    ]

