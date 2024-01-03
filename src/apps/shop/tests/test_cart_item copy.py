from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.shop.models import Order, OrderItem

class CartItemTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            ...
        )