from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.signals  # noqa: F401 — wire up audit log signals

        # Wire up notification signals
        from api.notification_signals import connect_notification_signals
        connect_notification_signals()
