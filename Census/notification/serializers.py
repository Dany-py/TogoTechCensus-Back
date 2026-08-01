from rest_framework import serializers
from .models import Notification, NotificationPreference, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'recipient_username',
            'notification_type',
            'type_display',
            'title',
            'message',
            'priority',
            'priority_display',
            'is_read',
            'is_urgent',
            'created_at',
            'read_at',
            'action_url',
            'extra_data',
        ]
        read_only_fields = [
            'id',
            'recipient',
            'created_at',
            'read_at',
            'is_urgent',
            'type_display',
            'priority_display',
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'type_display',
            'title',
            'priority',
            'priority_display',
            'is_read',
            'is_urgent',
            'created_at',
            'action_url',
        ]
        read_only_fields = fields


class NotificationMarkAsReadSerializer(serializers.Serializer):
    """Serializer to mark notification as read"""
    is_read = serializers.BooleanField()
    
    def update(self, instance, validated_data):
        if validated_data['is_read']:
            instance.mark_as_read()
        else:
            instance.mark_as_unread()
        return instance


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    email_frequency_display = serializers.CharField(
        source='get_email_frequency_display',
        read_only=True
    )
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'user',
            'user_username',
            'email_on_project_approved',
            'email_on_project_rejected',
            'email_on_submission_review',
            'email_on_comment',
            'email_on_mention',
            'app_notifications_enabled',
            'email_frequency',
            'email_frequency_display',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
        ]
        read_only_fields = [
            'id',
            'user',
            'user_username',
        ]


class NotificationLogSerializer(serializers.ModelSerializer):
    delivery_method_display = serializers.CharField(
        source='get_delivery_method_display',
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_title = serializers.CharField(
        source='notification.title',
        read_only=True
    )
    
    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'notification',
            'notification_title',
            'delivery_method',
            'delivery_method_display',
            'status',
            'status_display',
            'error_message',
            'created_at',
            'sent_at',
        ]
        read_only_fields = fields
