from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import NotificationPreference

User = get_user_model()


@receiver(post_save, sender=User)
def create_notification_preference(sender, instance, created, **kwargs):
    """Create notification preference for new user"""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_notification_preference(sender, instance, **kwargs):
    """Save notification preference when user is saved"""
    try:
        instance.notification_preference.save()
    except NotificationPreference.DoesNotExist:
        NotificationPreference.objects.create(user=instance)
