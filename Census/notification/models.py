from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


class NotificationQuerySet(models.QuerySet):
    """Custom QuerySet for Notifications"""
    
    def unread(self):
        return self.filter(is_read=False)
    
    def read(self):
        return self.filter(is_read=True)
    
    def for_user(self, user):
        return self.filter(recipient=user)
    
    def active(self):
        return self.filter(is_deleted=False)


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def unread(self):
        return self.get_queryset().unread()
    
    def read(self):
        return self.get_queryset().read()
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def active(self):
        return self.get_queryset().active()


class Notification(models.Model):
    """Model for managing system notifications"""
    
    NOTIFICATION_TYPES = [
        ('project_submitted', 'Project Submitted'),
        ('project_approved', 'Project Approved'),
        ('project_rejected', 'Project Rejected'),
        ('project_updated', 'Project Updated'),
        ('submission_review', 'Submission Under Review'),
        ('comment', 'New Comment'),
        ('reply', 'Reply to Comment'),
        ('mention', 'You were mentioned'),
        ('system', 'System Message'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Core fields
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='system'
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Priority and status
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium'
    )
    
    is_read = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Related objects - generic relations
    related_project = models.ForeignKey(
        'projects.Projects',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    related_submission = models.ForeignKey(
        'projects.Submissions',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Additional data as JSON for flexibility
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data related to the notification"
    )
    
    # Action URL
    action_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to redirect when notification is clicked"
    )
    
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['is_deleted']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title} ({self.recipient.username})"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    def delete_notification(self):
        """Soft delete notification"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])
    
    def restore_notification(self):
        """Restore soft-deleted notification"""
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])
    
    @property
    def is_urgent(self):
        """Check if notification has high priority"""
        return self.priority in ['high', 'urgent']


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    
    NOTIFICATION_FREQUENCY = [
        ('instant', 'Instant'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
        ('never', 'Never'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    
    # Email notifications
    email_on_project_approved = models.BooleanField(default=True)
    email_on_project_rejected = models.BooleanField(default=True)
    email_on_submission_review = models.BooleanField(default=True)
    email_on_comment = models.BooleanField(default=True)
    email_on_mention = models.BooleanField(default=True)
    
    # In-app notifications
    app_notifications_enabled = models.BooleanField(default=True)
    
    # Frequency settings
    email_frequency = models.CharField(
        max_length=20,
        choices=NOTIFICATION_FREQUENCY,
        default='instant'
    )
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    
    def should_send_email(self, notification_type):
        """Check if email should be sent for this notification type"""
        if not self.user.email:
            return False
        
        preference_map = {
            'project_approved': self.email_on_project_approved,
            'project_rejected': self.email_on_project_rejected,
            'submission_review': self.email_on_submission_review,
            'comment': self.email_on_comment,
            'mention': self.email_on_mention,
        }
        
        return preference_map.get(notification_type, False)
    
    def is_in_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled:
            return False
        
        current_time = timezone.now().time()
        return self.quiet_hours_start <= current_time <= self.quiet_hours_end


class NotificationLog(models.Model):
    """Log for notification delivery attempts"""
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('in_app', 'In-App'),
            ('push', 'Push Notification'),
        ]
    )
    
    status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS,
        default='pending'
    )
    
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
    
    def __str__(self):
        return f"{self.get_delivery_method_display()} - {self.get_status_display()}"
