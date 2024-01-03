from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shop'

    def ready(self):
        import apps.shop.signals  # Import the signals module