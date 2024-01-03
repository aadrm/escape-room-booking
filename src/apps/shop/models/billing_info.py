from django.db import models
from django.urls import reverse



class BillingInfo(models.Model):

    # Customer info
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # Billing address
    street = models.CharField(max_length=62, blank=True, null=True)
    street_number = models.CharField(max_length=8, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    postal_code = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        verbose_name = "BillingInfo"
        verbose_name_plural = "BillingInfos"

    def __str__(self):
        return str(self.email)

    def get_absolute_url(self):
        return reverse("BillingInfo_detail", kwargs={"pk": self.pk})
