
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Projects, Submissions, Categories, Technologies, Audiences, Authors

# Post save signal for Project's registration
@receiver(post_save, sender=Projects)
def post_save_project(sender, instance, created, **kwargs):
    if created:
        print(f"New post created: {instance.name}")
        Submissions.objects.create(
            project=instance,
            submitted_by=instance.user,
            reviewed_by=instance.user,
            review_notes="Première soumission"
        )
    else:
        print(f"Post updated: {instance.name}")