from rest_framework import permissions, viewsets

from ..models import Slot
from ..serializers import SlotSerializer

class  SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    permission_classes = [permissions.IsAuthenticated]