from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser



# Model Users
class Users(AbstractUser):
    class Role(models.TextChoices):
        USER = 'UR', _('utilisateur')
        MODERATOR = 'MR', _('moderateur')

    name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(max_length=100)
    role = models.CharField(max_length=2, choices=Role, default=Role.USER, db_index=True)
    subId = models.TextField(null=True, unique=True, db_index=True)
    provider = models.CharField(null=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}-{self.name} - {self.email} - {self.role}"