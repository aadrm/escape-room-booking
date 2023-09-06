from django.utils.translation import gettext_lazy as _

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

DAY_CHOICES = [
    (MONDAY, _('Mon')),
    (TUESDAY, _('Tue')),
    (WEDNESDAY, _('Wed')),
    (THURSDAY, _('Thu')),
    (FRIDAY, _('Fri')),
    (SATURDAY, _('Sat')),
    (SUNDAY, _('Sun')),
]
