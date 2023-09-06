from django.db import models
from django.utils.translation import gettext_lazy as _

from . import ProductGroup


class ProductGroupAppointment(ProductGroup):

    room = models.ForeignKey("appointments.Room", verbose_name=_("Room"), on_delete=models.CASCADE)


