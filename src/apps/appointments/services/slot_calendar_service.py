from datetime import date
from ..models import Slot


class SlotCalendarService:

    @staticmethod
    def get_days_with_slots_in_month(*, year, month):
        start_date = date(year, month, day=1)
        end_date = date(year, month + 1, day=1)

        slot_dates = (Slot.objects.filter(start__range=[start_date, end_date]))

        dates = set()
        for obj in slot_dates:
            dates.add(obj.start.date())

        print(dates)



