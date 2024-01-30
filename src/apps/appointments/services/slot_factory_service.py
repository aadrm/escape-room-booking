import logging
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from ..models import Slot

logger = logging.getLogger(__name__)

class SlotFactoryService:

    @staticmethod
    def create_slots_bound_to_schedule(
            *,
            schedule,
            start_date,
            end_date,
            days_of_week,
            start_time,
            duration_minutes,
            buffer_minutes,
            room,
            repeat_times,
        ):
        slots_to_save = []
        total_created = 0
        current_date = max(start_date, timezone.now().date())

        while current_date <= end_date:
            current_datetime = timezone.datetime.combine(current_date, start_time)

            if current_datetime.weekday() in days_of_week:
                for n in range(repeat_times):
                    slot = Slot(
                        start=current_datetime,
                        duration=duration_minutes,
                        buffer=buffer_minutes,
                        room=room,
                        schedule=schedule,
                    )
                    current_datetime += timedelta(minutes=duration_minutes + buffer_minutes)
                    try:
                        slot.full_clean()
                        slots_to_save.append(slot)
                        total_created += 1
                    except ValidationError as e:
                        logger.error(lambda: f'Error creating slot: {e}')

            current_date += timedelta(days=1)

        # not using bulk_create as it bypasses the custom save() method
        for slot in slots_to_save:
            slot.save()

        logger.info(lambda: f'finished processing. Totel created slots: {total_created}')