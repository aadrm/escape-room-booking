
from apps.shop.models import Order, OrderItem, Cart, BillingInfo
from .shop_settings_test_case import ShopSettingsTestCase

class OrderItemTestCase(ShopSettingsTestCase):

    def setUp(self):
        self.cart = Cart.objects.create()
        self.billing = BillingInfo.objects.create(email="jdoe@mail.com")
        self.order = Order.objects.create(
            cart=self.cart,
            billing_info=self.billing
        )

    def test_order_item_set_net_price_on_save(self):
        item = OrderItem.objects.create(
            reference='item',
            order=self.order,
            base_price=119,
            gross_price=119,
            vat_factor=0.19,
        )
        self.assertAlmostEqual(100, item.net_price)


