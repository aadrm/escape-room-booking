
from django.db import models
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):

    class Status(models.IntegerChoices):
        OPEN = 1
        COMPLETED = 2
        CANCELLED = 3

    status = models.IntegerField(choices=Status.choices)

    def __str__(self) -> str:
        return self.get_status_display()

