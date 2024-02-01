from decimal import Decimal
from apps.shop.models import BillingInfo, Cart, Order, OrderItem
from .shop_settings_test_case import ShopSettingsTestCase

class OrderTestCase(ShopSettingsTestCase):

    def setUp(self):
        cart1 = Cart.objects.create()
        billing1 = BillingInfo.objects.create(email="jdoe@mail.com")

        self.order = Order.objects.create(
            cart=cart1,
            billing_info=billing1
        )


        self.order.add_item(
            reference='item 1',
            base_price=100,
            gross_price=100,
            vat_factor=0.19,
        )

        OrderItem.objects.create(
            order=self.order,
            reference='item 2',
            base_price=100,
            gross_price=50,
            vat_factor=0.19,
        )

        cart2 = Cart.objects.create()
        billing2 = BillingInfo.objects.create(email="jdoe@mail.com")

        self.empty_order = Order.objects.create(
            cart=cart2,
            billing_info=billing2
        )

    def test_order_updating_on_signal_update_order_on_order_item(self):
        self.assertAlmostEqual(0, self.empty_order.base_total)
        item = self.empty_order.add_item(reference="item", base_price=10, gross_price=0, vat_factor=0)
        self.assertAlmostEqual(10, self.empty_order.base_total)
        item.base_price = 15
        item.save()
        self.assertAlmostEqual(15, self.empty_order.base_total)
        item.delete()
        self.assertAlmostEqual(0, self.empty_order.base_total)

    def test_calculate_and_set_base_total_if_0(self):
        self.assertEqual(0, self.empty_order.base_total)

    def test_calculate_and_set_base_total(self):
        self.assertEqual(200, self.order.base_total)

    def test_calculate_and_set_gross_total_if_0(self):
        self.assertEqual(0, self.empty_order.gross_total)

    def test_calculate_and_set_gross_total(self):
        self.assertEqual(150, self.order.gross_total)

    def test_calculate_and_set_net_total_if_0(self):
        self.assertEqual(0, self.empty_order.net_total)

    def test_calculate_and_set_net_total(self):
        self.assertEqual(Decimal(150 / 1.19).quantize(Decimal('0.00')), self.order.net_total)

    def test_calculate_and_set_vat_total_if_0(self):
        self.assertEqual(0, self.empty_order.vat_total)

    def test_calculate_and_set_vat_total(self):
        self.assertEqual(Decimal(150 - 150 / 1.19).quantize(Decimal('0.00')), self.order.vat_total)

    def test_discount_total_if_0(self):
        self.assertEqual(0, self.empty_order.vat_total)

    def test_discount_total(self):
        self.assertEqual(50, self.order.discount_total)