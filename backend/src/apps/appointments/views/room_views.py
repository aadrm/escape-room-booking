from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Room
from ..serializers import (
    RoomSerializer,
)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'], url_path='enabled')
    def get_active_rooms(self, request):

        enabled_rooms = Room.objects.filter(is_active=True)
        serializer = RoomSerializer(enabled_rooms, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
