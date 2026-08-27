import uuid
from django.db import models
from users.models import Users
from nanoid_field.fields import NanoidField

class Conversation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)
    anonymous_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    channel = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.uuid}-{self.user} - {self.is_active} - {self.is_deleted}"


class Message(models.Model):

    class Sender(models.TextChoices):
        USER = 'user', 'User'
        BOT = 'bot', 'Bot'

    id = NanoidField(primary_key=True, max_length=12, alphabet='0123456789abcdef')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=Sender.choices, db_index=True, null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']

    def __str__(self):
        return self.id
