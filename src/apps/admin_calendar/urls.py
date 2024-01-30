from django.urls import path
from .views import calendar_view

app_name = 'admin_calendar'

urlpatterns = [
    path('calendar/', calendar_view, name='calendar_view'),
    path('ajax-calendar/', calendar_view, name='ajax_admin_calendar')
]
