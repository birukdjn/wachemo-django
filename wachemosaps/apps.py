from django.apps import AppConfig


class WachemosapsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wachemosaps'

def ready(self):
    import wachemosaps.signals 