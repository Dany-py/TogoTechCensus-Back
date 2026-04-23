from django.db.models.signals import post_save, pre_save
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from utils import get_async_favicon
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from crum import get_current_user
from notification.trigger import trigger_notification
import os
from asgiref.sync import async_to_sync
from .models import Projects, Submissions, Updates
from notification.utils import NotificationService

User = get_user_model()

@receiver(pre_save, sender=Projects)
def pre_save_project_slug(sender, instance, **kwargs):
    if not instance.slug or instance.slug == '' or instance.slug == None:
        base_slug = slugify(instance.name)
        slug = base_slug
        qs = Projects.objects.filter(slug=slug)
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            slug = f"{base_slug}-{get_random_string(6)}"
        instance.slug = slug
    
    if instance.type:
        type = slugify(instance.type)
        instance.type = type


@receiver(post_save, sender=Projects)
def post_save_project( instance, created, **kwargs ):
    if getattr(instance, '_signal_handled', False):
        return

    user = get_current_user()

    if not user or not user.is_authenticated:
        print("User not authenticated !")
        return
    
    try:
        updates = {}

        if not instance.logo_url:
            url = get_async_favicon('github.com' if instance.type == 'open-source' else instance.website_url)
            if url:
                updates['logo_url'] = url

        if updates:
            Projects.objects.filter(pk=instance.pk).update(**updates)
    
        default_admin = User.objects.filter(username='admin_principal').first()
           
        if created:
            Submissions.objects.create(
                project=instance,
                submitted_by=user,
                reviewed_by=default_admin,
                review_notes="First submission"
            )
            notification = NotificationService.create_notification(
                recipient=user,
                notification_type='project_submitted',
                title= f"Your project '{instance.name}' has been registered",
                message=f'Congratulation! Your project has been successfully registered',
                priority='high',
            )
            trigger_notification(
                user_id=user.pk,
                type='update',
                title=notification.title,
                message=notification.message
            )
            print('Notification :', notification)
            send_mail(
                subject=f"Confirmation of your submission on {instance.name}",
                message=f"""Hello {user.name},

                    Thank you for submitting your project, {instance.name}, to our tech directory.

                    We have successfully received your information. Our team will now conduct a technical review to ensure the project meets our quality and relevance standards. This process typically takes seven (7) days.

                    You will receive a second email as soon as your listing has been approved and published.

                    In the meantime, please feel free to reach out if you have any questions.

                    Best regards,

                    The TogoTechCensus Team
                """,
                from_email=f"{os.getenv('EMAIL_SENDER')}",
                recipient_list=[f"{user.email}"],
                fail_silently=True,
            )
        else:
            # Mise à jour - optionnel selon ta logique métier
            notification = NotificationService.create_notification(
                recipient=user,
                notification_type='project_updated',
                title="Your project update has been registered",
                message=f"Your project '{instance.name}' update has been successfully registered",
            )
            trigger_notification(
                user_id=user.pk,
                type='update',
                title=notification.title,
                message=notification.message
            )
            print('Notification :', notification)

    except Exception as e:
        print(f"Error during signal processing: {e}")
