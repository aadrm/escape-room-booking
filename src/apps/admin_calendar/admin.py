from django.contrib import admin
from django.urls import reverse
from .urls import urlpatterns

class MyAdminSite(admin.AdminSite):
    app_name = 'admin_calendar'
    site_header = 'My Admin Site'
    site_title = 'My Admin Site'
    index_title = 'Welcome to My Admin Site'

    def get_urls(self):
        urls = super().get_urls()
        return urlpatterns + urls

my_admin_site = MyAdminSite(name='admin_calendar')
