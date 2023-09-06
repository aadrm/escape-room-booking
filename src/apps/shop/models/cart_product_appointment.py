
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import CartProduct, ProductGroupAppointment


class CartProductAppointment(CartProduct):
    slot = models.ForeignKey("appointments.Slot", verbose_name=_("slot"), on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __str__(self) -> str:
        return super().__str__() + self.slot.__str__()