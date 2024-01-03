from django.utils import timezone
from django.utils.timezone import timedelta


from apps.appointments.models import Slot, Room
from apps.shop.models import Cart, Coupon, Product, ProductGroupAppointment, ProductGroupCoupon
from apps.shop.services import CartToOrderService
from .shop_settings_test_case import ShopSettingsTestCase


class CartToOrderServiceTestCase(ShopSettingsTestCase):

    def setUp(self):
        self.cart = Cart.objects.create()

        room = Room.objects.create(name="room1")
        slot = Slot.objects.create(
            start=timezone.now() + timedelta(days=1),
            room=room
        )
        appointment_group = ProductGroupAppointment.objects.create(room=room)
        coupon_group = ProductGroupCoupon.objects.create(shipping_cost=8)
        appointment_product = Product.objects.create(
            name="game",
            base_price=10,
            product_group=appointment_group
        )
        coupon_product = Product.objects.create(
            name="coupon",
            base_price=5,
            product_group=coupon_group
        )

        self.cart.add_item_appointment(appointment_product, slot)
        self.cart.add_item_coupon(coupon_product)

    def test_cart_to_order(self):
        self.cart.save()
        return True