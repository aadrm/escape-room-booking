
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import CartItem, ShopSettings


class CartItemAppointment(CartItem):
    slot = models.OneToOneField("appointments.Slot", verbose_name=_("slot"), related_name="cart_item_appointment", on_delete=models.CASCADE)
    set_aside_datum = models.DateTimeField(_("Expiry"), auto_now_add=True, editable=True)

    def expiry(self):
        return self.set_aside_datum + timezone.timedelta(minutes=ShopSettings.load().slot_set_aside_time)

    def is_expired(self):
        return self.expiry() < timezone.datetime.now()

    def is_booking_slot(self):
        return self.cart.is_completed()

    def is_reserving_slot(self):
        return self.cart.is_open() and not self.is_expired()

    def reset_expiry(self):
        self.set_aside_datum = timezone.now()
        self.save()

    def __str__(self) -> str:
        return super().__str__() + ' - ' + self.slot.__str__()
