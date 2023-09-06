from django.db import models
from django.utils.translation import gettext_lazy as _
from common.inheritance_cast_model import InheritanceCastModel

class ProductGroup(InheritanceCastModel):

    name = models.CharField(_("Name"), max_length=32)

    def __str__(self) -> str:
        return self.name
