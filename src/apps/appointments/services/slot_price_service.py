from django.db.models import Min
from . import SlotAvailabilityService
from ..models import AppointmentsSettings


class SlotPriceService:

    @staticmethod
    def get_slot_lowest_base_price(slot):
        groups = slot.room.productgroupappointment_set.all()
        starting_price = groups.aggregate(Min('product__base_price'))['product__base_price__min']
        return starting_price

    @staticmethod
    def get_slot_incentive_discount(slot):
        if SlotAvailabilityService.is_parallel_slot_booked(slot):
            return AppointmentsSettings.load().parallel_incentive_discount
        if SlotAvailabilityService.is_adjacent_slot_booked(slot):
            return AppointmentsSettings.load().adjacent_incentive_discount
        else:
            return 0
