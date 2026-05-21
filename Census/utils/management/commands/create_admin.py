import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Creates the superuser automatically from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email    = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'dany@040501')

        if not password:
            self.stderr.write(self.style.ERROR("DJANGO_SUPERUSER_PASSWORD manquant."))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"'{username}' existe déjà."))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' créé avec succès."))