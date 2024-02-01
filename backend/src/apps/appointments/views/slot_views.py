from datetime import date
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import SlotCalendarService
from ..models import Slot
from ..serializers import (
    SlotSerializer,
    SlotWithAvailabilitySerializer,
    SlotWithStartingPriceSerializer,
    SlotWithStartingPriceAndAvailabilitySerializer
)


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='days_available/(?P<year>\d+)/(?P<month>\d+)')
    def get_days_available(self, request, year, month):
        year = int(year)
        month = int(month)

        available_days = SlotCalendarService.get_days_with_slots_in_month(year=year, month=month)

        serializer = DaysWithAvailableSlotsSerializer(
            [{'day': day, 'slots_available': True} for day in available_days],
            many=True
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='in_day/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)')
    def get_slots_for_day(self, request, year, month, day):
        year = int(year)
        month = int(month)
        day = int(day)

        query_date = date(year=year, month=month, day=day)
        slots_in_day = SlotCalendarService.get_slots_in_date(query_date)

        serializer = SlotWithStartingPriceAndAvailabilitySerializer(slots_in_day, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
