from ..models import Slot
from rest_framework import serializers

class SlotSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Slot
        fields = ['start']