from ..models import Slot
from ..services import SlotAvailabilityService
from rest_framework import serializers

class SlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slot
        fields = ['start', 'duration', 'room']


class SlotWithAvailabilitySerializer(SlotSerializer):
    visible = serializers.SerializerMethodField()

    class Meta(SlotSerializer.Meta):
        fields = SlotSerializer.Meta.fields + ['visible']

    def get_visible(self, instance):
        return not SlotAvailabilityService.is_hidden(instance)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        visibility = self.get_visible(instance)
        representation['visible'] = visibility
        return representation

class SlotWithStartingPriceSerializer(SlotSerializer):
    from_price = serializers.FloatField()

    class Meta(SlotSerializer.Meta):
        fields = SlotSerializer.Meta.fields + ['visible']

    def get_from_price(self, instance):
        return

class DaysWithAvailableSlotsSerializer(serializers.Serializer):
    day = serializers.DateField()
    slots_available = serializers.BooleanField()
