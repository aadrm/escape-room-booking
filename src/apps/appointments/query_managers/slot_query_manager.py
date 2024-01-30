from datetime import datetime, date
from django.db.models.query import QuerySet
from apps.appointments.models import Slot


class SlotQueryManager:

    @staticmethod
    def get_slots_by_block_end_between_datetimes(after: datetime, before: datetime) -> QuerySet:
        return Slot.objects.filter(block_end__gte=after, block_end__lte=before)

    @staticmethod
    def get_slots_by_start_between_datetimes(after: datetime, before: datetime) -> QuerySet:
        return Slot.objects.filter(start__range=[after, before])

    @staticmethod
    def get_slots_that_touch_period_between_datetimes(after: datetime, before: datetime) -> QuerySet:
        return Slot.objects.filter(block_end__gte=after, start__lte=before)

    @staticmethod
    def get_slots_in_day(a_date: date) -> QuerySet:
        return Slot.objects.filter(start__date=a_date)
