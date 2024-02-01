from django.test import TestCase
from django.utils import timezone
from apps.shop.models import Coupon, ShopSettings, Product, ProductGroup  # Import your models here


class CouponTestCase(TestCase):
    def setUp(self):
        # Create a ShopSettings instance with default values for testing
        self.coupon_default_days = 30
        self.coupon_default_length = 4
        self.coupon_default_chars = 'A'

        self.product1 = Product.objects.create(name='Product 1')
        self.product2 = Product.objects.create(name='Product 2')

        self.shop_settings = ShopSettings.objects.create(
            default_coupon_validity_in_days=self.coupon_default_days,
            default_coupon_code_length=self.coupon_default_length,
            default_coupon_code_chars=self.coupon_default_chars
        )

    def test_random_coupon_code_generation(self):
        # Test if a random coupon code is generated
        coupon = Coupon.objects.create()

        # Check if the auto generated code is generated according to default settings
        self.assertEqual(len(coupon.code), self.coupon_default_length)
        self.assertTrue(coupon.code.isupper())
        self.assertEqual(coupon.code, 'AAAA')

    def test_default_expiry_calc(self):
        # Test if the default expiry calculation is correct
        coupon = Coupon.objects.create()
        expiration_date = coupon.expiration_date
        today = timezone.now().date()

        # Check if the expiry date is 30 days from today
        self.assertEqual(expiration_date, today + timezone.timedelta(days=self.coupon_default_days))

    def test_applicable_products_with_products_included(self):
        # Test if applicable products are returned when products_included is not empty
        coupon = Coupon.objects.create()
        coupon.products_included.add(self.product1, self.product2)

        applicable_products = coupon._applicable_products()

        self.assertEqual(list(applicable_products), [self.product1, self.product2])

    def test_applicable_products_without_products_included(self):
        # Test if all products are returned when products_included is empty
        coupon = Coupon.objects.create()

        applicable_products = coupon._applicable_products()

        self.assertEqual(list(applicable_products), [self.product1, self.product2])

    def test_is_applicable_to_product(self):
        # Test if is_applicable_to_product returns True for an applicable product
        coupon = Coupon.objects.create()
        coupon.products_included.add(self.product1)

        is_applicable = coupon.is_applicable_to_product(self.product1)

        self.assertTrue(is_applicable)

    def test_is_not_applicable_to_product(self):
        # Test if is_applicable_to_product returns False for a non-applicable product
        coupon = Coupon.objects.create()

        coupon.products_included.add(self.product1)

        is_applicable = coupon.is_applicable_to_product(self.product2)

        self.assertFalse(is_applicable)