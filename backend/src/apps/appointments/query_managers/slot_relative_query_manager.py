from django.db.models.query import QuerySet
from django.utils.timezone import timedelta

from .slot_query_manager import SlotQueryManager
from ..models import AppointmentsSettings


class SlotRelativeQueryManager:
    """
    The `SlotRelativeQueryManager` provides methods for retrieving slots related to a given slot.

    Overview:
    This service offers various methods to retrieve slots based on different criteria such as temporal
    relationships, proximity, and overlap. It assists in querying and managing slots in the system.
    Each method returns a Django `QuerySet` of slots based on specific criteria.

    Glossary (notice that only same day slots fall in the scope):
    preceding - slots that end within the time set in settings before the start of the reference slot
    following - slots that start within the time set in settings after the end of the reference slot
    adjacent - adjacent is a union of preceding and following
    parallel - slots that start within the window of time (before and after) of the time site in settings
               from the start of the reference slot
    distant - slots which block time is as far as the time set in settings from the block time of the reference slot
    near - the rest of the slots in the day that are not distant

    Note: The service relies on the `SlotQueryManager` and `AppointmentsSettings` for querying the database
    and obtaining configuration settings, respectively.
    """

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
    def get_adjacent_slots(slot) -> QuerySet:
        preceding = SlotRelativeQueryManager.get_preceding_slots(slot).order_by()
        following = SlotRelativeQueryManager.get_following_slots(slot).order_by()
        return preceding.union(following)

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
        near_slots = SlotRelativeQueryManager.get_near_slots(slot)
        day_slots = SlotRelativeQueryManager.get_same_date_slots(slot)
        return day_slots.exclude(pk__in=near_slots.values('pk'))
