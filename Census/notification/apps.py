from django.apps import AppConfig

class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'
    verbose_name = 'Notifications'
    
    def ready(self):
        import notification.signals