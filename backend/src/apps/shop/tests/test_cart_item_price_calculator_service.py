from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.shop.services import CartItemPriceCalculatorService
from apps.shop.models import Cart, Coupon, Product, ProductGroupCoupon
from apps.appointments.models import Slot, Room

class CartItemTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create()
        self.room = Room.objects.create(
            name="room"
        )
        self.slot = Slot.objects.create(
            room=self.room,
            start=timezone.now()
        )
        coupon_group = ProductGroupCoupon.objects.create(shipping_cost=8)
        self.coupon_product = Product.objects.create(
            name="coupon",
            base_price=5,
            product_group=coupon_group
        )
        self.product = Product.objects.create(
            name='myproduct',
            base_price=10.00
        )
        self.percent_coupon_20 = Coupon.objects.create(
            value=20,
            is_percent=True,
            apply_to_entire_cart=False,
        )
        self.absolute_coupon_15 = Coupon.objects.create(
            value=15,
            apply_to_entire_cart=True
        )
        self.absolute_coupon_2 = Coupon.objects.create(
            value=2,
            apply_to_entire_cart=True
        )
        self.coupon_with_minimum_spend = Coupon.objects.create(
            value=10,
            apply_to_entire_cart=True,
            minimum_spend=10.1
        )

    def test_cart_item_price_no_coupons(self):
        cart_item = self.cart.add_item_appointment(self.product, slot=self.slot)
        price = CartItemPriceCalculatorService.calculate_price(cart_item)
        self.assertEqual(price, 10.00)

    def test_cart_item_price_with_shipping_no_coupons(self):
        cart_item = self.cart.add_item_coupon(product=self.coupon_product)
        price = CartItemPriceCalculatorService.calculate_price(cart_item)
        self.assertEqual(price, 13.00)

    def test_cart_item_price_20_percent_discount_coupon(self):
        self.cart.add_coupon(self.percent_coupon_20)
        cart_item = self.cart.add_item_appointment(self.product, self.slot)
        self.assertEqual(8.00, CartItemPriceCalculatorService.calculate_price(cart_item))

    def test_cart_item_price_20_percent_discount_single_item_coupn(self):
        self.cart.add_coupon(self.percent_coupon_20)
        cart_item_1 = self.cart.add_item_appointment(self.product, self.slot)
        cart_item_2 = self.cart.add_item_coupon(self.coupon_product)
        self.assertEqual(8.00, CartItemPriceCalculatorService.calculate_price(cart_item_1))
        self.assertEqual(13.00, CartItemPriceCalculatorService.calculate_price(cart_item_2))

    def test_cart_item_price_coupon_overflow(self):
        self.cart.add_coupon(self.absolute_coupon_15)
        cart_item_1 = self.cart.add_item_appointment(self.product, self.slot)
        cart_item_2 = self.cart.add_item_coupon(self.coupon_product)
        self.assertEqual(0, CartItemPriceCalculatorService.calculate_price(cart_item_1))
        self.assertEqual(8.00, CartItemPriceCalculatorService.calculate_price(cart_item_2))

    def test_cart_item_price_apply_absolute_then_percent_coupons(self):
        self.cart.add_coupon(self.percent_coupon_20)
        self.cart.add_coupon(self.absolute_coupon_2)
        cart_item_1 = self.cart.add_item_appointment(self.product, self.slot)
        self.assertAlmostEqual(Decimal(6.40), CartItemPriceCalculatorService.calculate_price(cart_item_1))

    def test_cart_item_price_unaffected_if_cart_total_lower_than_coupon_minimum(self):
        self.cart.add_coupon(self.coupon_with_minimum_spend)
        cart_item_1 = self.cart.add_item_appointment(self.product, self.slot)
        self.assertEqual(10.00, CartItemPriceCalculatorService.calculate_price(cart_item_1))


