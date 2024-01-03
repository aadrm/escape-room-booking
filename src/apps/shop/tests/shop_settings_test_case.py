from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from apps.shop.models.shop_settings import ShopSettings


class ShopSettingsTestCase(TestCase):

    def setUp(self):
        self.shop_settings = ShopSettings.objects.create(
            default_coupon_code_length=8,
            default_coupon_validity_in_days=8,
            slot_set_aside_time=20,
            order_number_lower_limit=100000,
            order_number_upper_limit=999999
        )
