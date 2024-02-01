
from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'slots', views.SlotViewSet)
router.register(r'rooms', views.RoomViewSet)

app_name = 'appointments'

urlpatterns = [
    path('api/', include(router.urls))
]
