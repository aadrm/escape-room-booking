from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_on_order_item(sender, instance, **kwargs):
    order = instance.order
    order.calculate_and_set_base_total()
    order.calculate_and_set_gross_total()
    order.calculate_and_set_net_total()
    order.calculate_and_set_vat_total()
    order.save()