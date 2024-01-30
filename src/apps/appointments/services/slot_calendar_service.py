from datetime import date, timedelta
from django.utils import timezone

from ..models import Slot
from ..query_managers import SlotQueryManager


class SlotCalendarService:

    @staticmethod
    def get_days_with_slots_in_month(*, year, month):
        start_date = date(year, month, day=1)
        end_date = date(year, (month % 12) + 1 , day=1)

        slot_dates = SlotQueryManager.get_slots_by_start_between_datetimes(start_date, end_date)

        dates = set()
        for obj in slot_dates:
            dates.add(obj.start.date())

        return dates

    @staticmethod
    def get_slots_in_date(aDate):
        SlotQueryManager.get_slots_in_day(aDate)




