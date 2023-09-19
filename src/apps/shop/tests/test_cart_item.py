from decimal import Decimal
from django.test import TestCase
from apps.shop.models import Cart, Coupon, CartCoupon, CartItem, Product

class CartItemTestCase(TestCase):
    def setUp(self):
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

    def test_cart_item_price_no_coupons(self):
        cart = Cart.objects.create()
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        self.assertEqual(cart_item.price, 10.00)

    def test_cart_item_price_20_percent_discount_coupon(self):
        cart = Cart.objects.create()
        cart_coupon = CartCoupon.objects.create(
            cart=cart,
            coupon=self.percent_coupon_20
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        self.assertEqual(cart_item.price, 8.00)

    def test_cart_item_price_20_percent_discount_single_item_coupn(self):
        cart = Cart.objects.create()
        cart_coupon = CartCoupon.objects.create(
            cart=cart,
            coupon=self.percent_coupon_20
        )
        cart_item_1 = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        cart_item_2 = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        self.assertEqual(cart_item_1.price, 8.00)
        self.assertEqual(cart_item_2.price, 10.00)

    def test_cart_item_price_coupon_overflow(self):
        cart = Cart.objects.create()
        cart_coupon = CartCoupon.objects.create(
            cart=cart,
            coupon=self.absolute_coupon_15
        )
        cart_item_1 = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        cart_item_2 = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        self.assertEqual(cart_item_1.price, 0.00)
        self.assertEqual(cart_item_2.price, 5.00)

    def test_cart_item_price_apply_absolute_then_percent_coupons(self):
        cart = Cart.objects.create()
        cart_coupon = CartCoupon.objects.create(
            cart=cart,
            coupon=self.percent_coupon_20
        )
        cart_coupon = CartCoupon.objects.create(
            cart=cart,
            coupon=self.absolute_coupon_2
        )
        cart_item_1 = CartItem.objects.create(
            cart=cart,
            product=self.product,
        )
        self.assertAlmostEqual(cart_item_1.price, Decimal(6.40))

