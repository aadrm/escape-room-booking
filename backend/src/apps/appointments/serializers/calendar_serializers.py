from rest_framework import serializers


class DaysWithAvailableSlotsSerializer(serializers.Serializer):
    day = serializers.DateField()
    slots_available = serializers.BooleanField()