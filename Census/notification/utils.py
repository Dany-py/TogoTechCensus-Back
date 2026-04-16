"""
Utility functions for managing notifications
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Notification, NotificationLog
from typing import Optional, Dict, Any

User = get_user_model()


class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def create_notification(
        recipient: User,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'medium',
        related_project=None,
        related_submission=None,
        action_url: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            recipient: User object who receives the notification
            notification_type: Type of notification (must be in NOTIFICATION_TYPES)
            title: Notification title
            message: Notification message body
            priority: Priority level ('low', 'medium', 'high', 'urgent')
            related_project: Optional related Projects instance
            related_submission: Optional related Submissions instance
            action_url: Optional URL to redirect on click
            extra_data: Optional additional data as dict
            
        Returns:
            The created Notification instance
            
        Raises:
            ValidationError: If invalid notification_type or priority
        """
        # Validate notification type
        valid_types = [t[0] for t in Notification.NOTIFICATION_TYPES]
        if notification_type not in valid_types:
            raise ValidationError(
                f"Invalid notification_type: {notification_type}. "
                f"Must be one of {valid_types}"
            )
        
        # Validate priority
        valid_priorities = [p[0] for p in Notification.PRIORITY_LEVELS]
        if priority not in valid_priorities:
            raise ValidationError(
                f"Invalid priority: {priority}. "
                f"Must be one of {valid_priorities}"
            )
        
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_project=related_project,
            related_submission=related_submission,
            action_url=action_url,
            extra_data=extra_data or {},
        )
        
        return notification
    
    @staticmethod
    def create_bulk_notifications(
        recipients,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'medium',
        action_url: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> list:
        """
        Create multiple notifications for different recipients with the same content
        
        Args:
            recipients: Iterable of User objects
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            action_url: Optional URL to redirect on click
            extra_data: Optional additional data
            
        Returns:
            List of created Notification instances
        """
        notifications = []
        for recipient in recipients:
            notification = NotificationService.create_notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                action_url=action_url,
                extra_data=extra_data,
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def send_project_approved_notification(user, project):
        """Send notification when project is approved"""
        return NotificationService.create_notification(
            recipient=user,
            notification_type='project_approved',
            title=f'Project "{project.name}" has been approved!',
            message=f'Congratulations! Your project "{project.name}" has been approved and is now visible in the directory.',
            priority='high',
            related_project=project,
            action_url=f'{project.get_absolute_url()}' if hasattr(project, 'get_absolute_url') else None,
        )
    
    @staticmethod
    def send_project_rejected_notification(user, project, reason: str = ''):
        """Send notification when project is rejected"""
        message = f'Your project "{project.name}" has been rejected.'
        if reason:
            message += f'\n\nReason: {reason}'
        
        return NotificationService.create_notification(
            recipient=user,
            notification_type='project_rejected',
            title=f'Project "{project.name}" was not approved',
            message=message,
            priority='high',
            related_project=project,
            extra_data={'reason': reason},
        )
    
    @staticmethod
    def send_project_submitted_notification(user, project):
        """Send notification when project is submitted"""
        return NotificationService.create_notification(
            recipient=user,
            notification_type='project_submitted',
            title=f'Project "{project.name}" submitted successfully',
            message=f'Your project "{project.name}" has been submitted for review. You will receive an email once the review is complete.',
            priority='medium',
            related_project=project,
        )
    
    @staticmethod
    def send_submission_review_notification(user, project):
        """Send notification when submission is under review"""
        return NotificationService.create_notification(
            recipient=user,
            notification_type='submission_review',
            title=f'Project "{project.name}" is under review',
            message=f'Your project "{project.name}" is now under review by our team. This typically takes 7 days.',
            priority='medium',
            related_project=project,
        )
    
    @staticmethod
    def log_notification_delivery(
        notification: Notification,
        delivery_method: str,
        status: str = 'pending',
        error_message: str = '',
    ) -> NotificationLog:
        """
        Log a notification delivery attempt
        
        Args:
            notification: The Notification instance
            delivery_method: Method used ('email', 'in_app', 'push')
            status: Delivery status ('pending', 'sent', 'failed')
            error_message: Error message if delivery failed
            
        Returns:
            The created NotificationLog instance
        """
        return NotificationLog.objects.create(
            notification=notification,
            delivery_method=delivery_method,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def mark_user_notifications_as_read(user):
        """Mark all unread notifications for a user as read"""
        count = 0
        for notification in user.notifications.unread():
            notification.mark_as_read()
            count += 1
        return count
    
    @staticmethod
    def delete_old_notifications(days: int = 90):
        """Delete old read notifications"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()
        
        return deleted_count
