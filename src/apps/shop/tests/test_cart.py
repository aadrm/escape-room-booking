from django.test import TestCase
from django.utils import timezone
from apps.appointments.models import Slot, Room
from apps.shop.models import Cart, Coupon, Product


class CartTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create()
        self.coupon1 = Coupon.objects.create()
        self.coupon2 = Coupon.objects.create()

        self.room = Room.objects.create(name="room1")
        self.slot1 = Slot.objects.create(
            start=timezone.datetime.now() + timezone.timedelta(days=1),
            room=self.room
        )
        self.product1 = Product.objects.create(name="slot product 1", base_price=10)
        self.product2 = Product.objects.create(name="coupon product 1")

    def test_add_coupon_to_cart(self):
        self.cart.add_coupon(self.coupon1)
        self.cart.add_coupon(self.coupon2)
        self.cart.refresh_from_db()
        self.assertIn(self.coupon1, self.cart.get_coupons())
        self.assertIn(self.coupon2, self.cart.get_coupons())

    def test_coupon_can_be_added_once(self):
        self.cart.add_coupon(self.coupon1)
        self.cart.add_coupon(self.coupon1)
        self.assertEquals(self.cart.coupons.count(), 1)


    def test_add_item(self):
        self.cart.add_item_appointment(self.product1, self.slot1)
        self.cart.add_item_coupon(self.product2)
        self.assertIn(self.slot1, self.cart.get_slots())
        self.assertEqual(self.product1, self.cart.get_cartitemappointment_set().first().product)
        self.assertEqual(self.product2, self.cart.get_cartitemcoupon_set().first().product)

    def test_add_item_reserved_slot_not_added(self):
        self.cart.add_item_appointment(self.product1, self.slot1)
        self.cart.add_item_appointment(self.product1, self.slot1)
        self.assertEqual(1, self.cart.get_cartitemappointment_set().count())

    def test_remove_expired_appointments(self):
        appointment_item = self.cart.add_item_appointment(self.product1, self.slot1)
        appointment_item.set_aside_datum = timezone.now() - timezone.timedelta(days=1)
        appointment_item.save()
        self.assertEqual(0, self.cart.get_cartitemappointment_set().count())

    def test_calculate_total_base_price(self):
        self.cart.add_item_appointment(self.product1, self.slot1)
        total_base_price = self.cart.get_total_base_price()
        self.assertAlmostEqual(10, total_base_price)


