from datetime import timedelta
from django.utils import timezone
from django.db.models import (Model,
                              DateTimeField,
                              PositiveSmallIntegerField,
                              ForeignKey,
                              BooleanField,
                              CASCADE,
                              SET_NULL)


class Slot(Model):
    """A bookable slot in the calendar, slots are created automatically when saving Schedule objects and are
    not supposed to be modified directly by the user

    Attributes:
        start: Datetime.
        duration: Int in minutes.
        interval: Int in minutes, buffer that prevents new slots being created with a start too close to the previous
        schedule: relation to Schedule Objects
        protect: Bool, if true, the slot is fixed and stops being affected by it's schedule
    """
    start = DateTimeField(_("Start"), auto_now=False, auto_now_add=False)
    duration = PositiveSmallIntegerField(_("Duration"), default=60)
    buffer = PositiveSmallIntegerField(_("interval"), default=30)
    room = ForeignKey("booking.Room", verbose_name=_("room"), on_delete=CASCADE)
    schedule = ForeignKey("booking.Schedule", verbose_name=_("schedule"), related_name=("slots"), on_delete=SET_NULL, null=True)
    protect = BooleanField("protect", null=True)
    product_family = ForeignKey("booking.ProductFamily", verbose_name=_("ProductFamily"), on_delete=CASCADE, null=True, blank=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        ordering = ['room', 'start']

    @property
    def end(self):
        return self.start + timedelta(minutes=self.duration + self.interval)

    @property
    def session_end(self):
        return self.start + timedelta(minutes=self.duration)

    @property
    def is_available(self):
        return not self.is_reserved() \
            and not self.is_affected_by_buffer() \
            and not self.is_disabled \
            and self._is_future

    @property
    def is_available_to_staff(self):
        return not self.is_reserved()

    def is_booked(self):
        for item in self.cart_items.all():
            if item.status > 0:
                return True

    def is_reserved(self):
        for item in self.cart_items.all():
            if item.status > 0 or (item.status == 0 and item.item_expiry() >= timezone.now()):
                return True
        return False

    def is_affected_by_buffer(self):
        return not self.is_future_of_buffer() and not self.is_adjacent_after_to_taken_slot()

    # def is_future_of_buffer(self):
    #     this_moment = timezone.now()
    #     buffer = this_moment + timedelta(minutes=get_booking_settings().slot_buffer_time)
    #     return self.start > buffer

    def _is_future(self):
        return self.start > timezone.now()

    def is_adjacent_after_to_taken_slot(self):
        slots = self.get_before_after_minutes_slots(20, 110)
        for slot in slots:
            if slot.is_booked():
                return True
        return False

    def is_adjacent_to_taken_slot(self):
        slots = self.get_before_after_minutes_slots(110, 110)
        for slot in slots:
            if slot.is_booked():
                return True
        return False

    def is_parallel_to_taken_slot(self):
        slots = self.get_before_after_minutes_slots(20, 20)
        for slot in slots:
            if slot.is_booked():
                return True
        return False

    def get_before_after_minutes_slots(self, before, after):
        """ Uses the start of sessions as reference
        """
        upper_bound = self.start + timedelta(minutes=before)
        lower_bound = self.start - timedelta(minutes=after)
        return Slot.objects.filter(start__lte=upper_bound, start__gte=lower_bound)

    def incentive_discount(self):
        if self.is_parallel_to_taken_slot():
            discount = get_booking_settings().incentive_discount_parallel_slots
        elif self.is_adjacent_to_taken_slot():
            discount = get_booking_settings().incentive_discount_adjacent_slots
        else:
            discount = 0
        return discount

    def __str__(self):
        return self.start.astimezone().strftime("%Y-%m-%d | %H:%M" )

    def save(self, *args, **kwargs):
        # booked_slots = Slot.objects.filter(booking__isnull=False)
        # TODO there's room for opmimisation here, the query calls for slots in the same day
        # this courd be improved into just checking if the query exists for specific slots
        slots = Slot.objects.filter(start__date=self.start.date(), room=self.room)
        slots = slots.exclude(pk=self.pk)

        slot_collides = False

        for slot in slots:
            if self.is_same_time(slot):
                slot_collides = True
        if slot_collides:
            print (f'{self} collided')
        else:
            n = datetime.today()
            today_date = datetime(n.year, n.month, n.day, 0, 0, 0, 0)
            today_date = make_aware(today_date)
            # saves if slot is in the future
            if self.start > today_date or self.cart_items.all() or self.protect:
                super(Slot, self).save(*args, **kwargs)
            else:
                pass



    def is_same_time(self, other):
        """compares a Slot with other Slot, if there is supperpossision in the scheduled times then returns true"""
        if self.start <= other.start and self.end <= other.start or self.start >= other.end and self.end >= other.end:
            return False
        else:
            return True
