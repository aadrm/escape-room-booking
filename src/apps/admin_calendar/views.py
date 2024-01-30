from django.contrib import admin
from django.shortcuts import render
from apps.appointments.models import Slot


def get_admin_context(request):

    context = {
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
        'has_permission': admin.site.has_permission(request),
        # available apps is used because the app_list is overwritten by the nav bar
        # template using the available_apps context variable
        'available_apps': admin.site.get_app_list(request),
        'username': request.user.username,
        'is_nav_sidebar_enabled': admin.site.enable_nav_sidebar,
    }

    return context


def calendar_view(request):
    slots = Slot.objects.all()
    context = {}
    context.update({'title': 'Calendar'})
    context.update({'slots': slots})
    # context.update(get_admin_context(request))
    return render(request, 'admin/calendar_view.html', context)