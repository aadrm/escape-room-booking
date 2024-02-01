from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Shift(models.Model):

    employee = models.ForeignKey(User, verbose_name=_("Employee"), on_delete=models.SET_NULL, null=True, blank=True)
    shift_date = models.DateField(verbose_name=_("Date"))

    class Meta:
        verbose_name = _("Shift")
        verbose_name_plural = _("Shifts")

    def __str__(self):
        return self.employee.__str__()

    def _same_date_shifts(self):
        return Shift.objects.filter(shift_date__exact=self.shift_date).exclude(pk=self.pk)

    def save(self, *args, **kwargs):
        if self._same_date_shifts().exists():
            raise ValidationError("Date already assigned")
        else:
            super().save(*args, **kwargs)


