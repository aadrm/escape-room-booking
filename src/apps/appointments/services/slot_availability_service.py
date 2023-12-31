from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.timezone import timedelta

from ..query_managers import SlotQueryManager
from ..models import AppointmentsSettings



class SlotAvailabilityService:
    """
    There are different conditions that affect the state and availability of a slot:

    There are three main states a slot can have:

    Unavailable, Hidden, Available

    + unavailable
        - is_booked (in a cart where the order has been completed)
        or
        - not is_start_in_future

    + hidden (A staff member could assign a slot to a booking)
        - not unavailable
        and
        - blocked (Blocked due to a combination of conditions)
            - not enabled
            - blocked by settings (prevent after date/days)
            - blocked by buffer
            - blocked by other bookings (smart calendar)
        or
        - reserved (in an "open" order and reserved for some time)

    + visible (Shows up in the calendar)
        - not hidden
    """
    @staticmethod
    def is_unavailable(slot) -> bool:
        return (
            SlotAvailabilityService.is_booked(slot) or
            not SlotAvailabilityService.is_start_in_future(slot)
        )

    @staticmethod
    def is_hidden(slot) -> bool:
        return (
            SlotAvailabilityService.is_blocked(slot) and
            not SlotAvailabilityService.is_unavailable(slot)
        )

    @staticmethod
    def is_blocked(slot) -> bool:
        return (
            not slot.is_enabled or
            SlotAvailabilityService.is_blocked_by_buffer(slot) or
            SlotAvailabilityService.is_blocked_by_settings(slot) or
            SlotAvailabilityService.is_blocked_by_booked_adjacent_slots(slot) or
            SlotAvailabilityService.is_blocked_by_booked_distant_slots(slot)
        )

    @staticmethod
    def is_reserved(slot) -> bool:
        return hasattr(slot, 'cart_item_appointment') \
            and slot.cart_item_appointment.is_reserving_slot()

    @staticmethod
    def is_booked(slot) -> bool:
        return hasattr(slot, 'cart_item_appointment') \
            and slot.cart_item_appointment.is_booking_slot()

    @staticmethod
    def is_at_least_one_slot_taken(slot_queryset: QuerySet) -> bool:
        for slot in slot_queryset:
            if SlotAvailabilityService.is_booked(slot):
                return True
        return False

    @staticmethod
    def taken_slots_count(slot_queryset: QuerySet) -> int:
        count = 0
        for slot in slot_queryset:
            if SlotAvailabilityService.is_booked(slot):
                count += 1
        return count

    @staticmethod
    def is_future_of_buffer(slot) -> bool:
        this_moment = timezone.now()
        buffer = this_moment + timedelta(minutes=AppointmentsSettings.load().buffer_in_minutes)
        return slot.start > buffer

    @staticmethod
    def get_same_date_slots(slot) -> QuerySet:
        slot_date = slot.start.date()
        return SlotQueryManager.get_slots_in_day(slot_date)

    @staticmethod
    def get_preceding_slots(slot) -> QuerySet:
        minutes = AppointmentsSettings.load().adjacent_slot_frame_in_minutes
        after_datetime = slot.start - timedelta(minutes=minutes)
        before_datetime = slot.start + timedelta(minutes=minutes)
        return SlotQueryManager.get_slots_by_block_end_between_datetimes(after_datetime, before_datetime)

    @staticmethod
    def get_following_slots(slot) -> QuerySet:
        minutes = AppointmentsSettings.load().adjacent_slot_frame_in_minutes
        after_datetime = slot.block_end - timedelta(minutes=minutes)
        before_datetime = slot.block_end + timedelta(minutes=minutes)
        return SlotQueryManager.get_slots_by_start_between_datetimes(after_datetime, before_datetime)

    @staticmethod
    def get_parallel_slots(slot) -> QuerySet:
        minutes = AppointmentsSettings.load().parallel_slot_frame_in_minutes
        after_datetime = slot.start - timedelta(minutes=minutes)
        before_datetime = slot.start + timedelta(minutes=minutes)
        return SlotQueryManager.get_slots_by_start_between_datetimes(after_datetime, before_datetime)

    @staticmethod
    def get_near_slots(slot) -> QuerySet:
        minutes = AppointmentsSettings.load().booked_distant_slots_block_minutes
        after_datetime = slot.start - timedelta(minutes=minutes)
        before_datetime = slot.block_end + timedelta(minutes=minutes)
        return SlotQueryManager.get_slots_that_touch_period_between_datetimes(after_datetime, before_datetime)

    @staticmethod
    def get_distant_slots(slot) -> QuerySet:
        near_slots = SlotAvailabilityService.get_near_slots(slot)
        day_slots = SlotAvailabilityService.get_same_date_slots(slot)
        return day_slots.exclude(pk__in=near_slots.values('pk'))

    @staticmethod
    def is_preceding_slot_booked(slot) -> bool:
        slots = SlotAvailabilityService.get_preceding_slots(slot)
        return SlotAvailabilityService.is_at_least_one_slot_taken(slots)

    @staticmethod
    def is_parallel_slot_booked(slot) -> bool:
        slots = SlotAvailabilityService.get_parallel_slots(slot)
        return SlotAvailabilityService.is_at_least_one_slot_taken(slots)

    @staticmethod
    def is_parallel_booked_slot_count_blocking(slot) -> bool:
        parallel_block_count = AppointmentsSettings.load().booked_parallel_slots_blocking_count
        parallel_slots = SlotAvailabilityService.get_parallel_slots(slot)
        return SlotAvailabilityService.taken_slots_count(parallel_slots) >= parallel_block_count

    @staticmethod
    def is_adjacent_booked_slot_count_blocking(slot) -> bool:
        adjacent_block_count = AppointmentsSettings.load().booked_adjacent_slots_blocking_count
        preceding_slots = SlotAvailabilityService.get_preceding_slots(slot)
        following_slots = SlotAvailabilityService.get_following_slots(slot)
        return SlotAvailabilityService.taken_slots_count(preceding_slots) >= adjacent_block_count or \
            SlotAvailabilityService.taken_slots_count(following_slots) >= adjacent_block_count

    @staticmethod
    def is_distant_slot_booked(slot) -> bool:
        distant_slots = SlotAvailabilityService.get_distant_slots(slot)
        return SlotAvailabilityService.is_at_least_one_slot_taken(distant_slots)

    @staticmethod
    def is_near_slot_booked(slot) -> bool:
        near_slots = SlotAvailabilityService.get_near_slots(slot)
        return SlotAvailabilityService.is_at_least_one_slot_taken(near_slots)

    @staticmethod
    def is_blocked_by_booked_distant_slots(slot) -> bool:
        return SlotAvailabilityService.is_distant_slot_booked(slot) and \
            not SlotAvailabilityService.is_near_slot_booked(slot)

    @staticmethod
    def is_blocked_by_booked_adjacent_slots(slot) -> bool:
        return SlotAvailabilityService.is_parallel_booked_slot_count_blocking(slot) and \
            SlotAvailabilityService.is_adjacent_booked_slot_count_blocking(slot)

    @staticmethod
    def is_blocked_by_buffer(slot) -> bool:
        return not SlotAvailabilityService.is_future_of_buffer(slot) and \
            not SlotAvailabilityService.is_preceding_slot_booked(slot) and \
            not SlotAvailabilityService.is_parallel_slot_booked(slot)

    @staticmethod
    def is_start_in_future(slot) -> bool:
        return slot.start >= timezone.now().replace(second=0, microsecond=0)

    @staticmethod
    def is_blocked_by_settings(slot) -> bool:
        return slot.start.date() > AppointmentsSettings.load().get_earliest_slot_date_limit()


