from django.contrib import admin


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

