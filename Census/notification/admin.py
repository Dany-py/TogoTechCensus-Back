from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Notification, NotificationPreference, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'recipient',
        'notification_type_badge',
        'priority_badge',
        'is_read_badge',
        'created_at',
    ]
    
    list_filter = [
        'notification_type',
        'priority',
        'is_read',
        'is_deleted',
        'created_at',
    ]
    
    search_fields = [
        'title',
        'message',
        'recipient__username',
        'recipient__email',
    ]
    
    readonly_fields = [
        'created_at',
        'read_at',
        'updated_at',
        'rendered_message',
    ]
    
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient',),
        }),
        ('Content', {
            'fields': (
                'notification_type',
                'title',
                'message',
                'rendered_message',
                'priority',
            ),
        }),
        ('Status', {
            'fields': ('is_read', 'is_deleted'),
        }),
        ('Relations', {
            'fields': ('related_project', 'related_submission'),
            'classes': ('collapse',),
        }),
        ('Additional Info', {
            'fields': ('action_url', 'extra_data'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'soft_delete', 'restore']
    
    date_hierarchy = 'created_at'
    
    def notification_type_badge(self, obj):
        """Display notification type as a colored badge"""
        colors = {
            'project_submitted': '#0066cc',
            'project_approved': '#00cc44',
            'project_rejected': '#ff3333',
            'project_updated': '#ffaa00',
            'submission_review': '#ff9900',
            'comment': '#6600cc',
            'reply': '#9900cc',
            'mention': '#ff6600',
            'system': '#999999',
        }
        color = colors.get(obj.notification_type, '#cccccc')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'
    
    def priority_badge(self, obj):
        """Display priority as a colored badge"""
        colors = {
            'low': '#cccccc',
            'medium': '#ffaa00',
            'high': '#ff6600',
            'urgent': '#ff3333',
        }
        color = colors.get(obj.priority, '#cccccc')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def is_read_badge(self, obj):
        """Display read status as a badge"""
        if obj.is_read:
            return format_html(
                '<span style="background-color: #00cc44; color: white; padding: 3px 8px; '
                'border-radius: 3px;">✓ Read</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #3366ff; color: white; padding: 3px 8px; '
                'border-radius: 3px;">● Unread</span>'
            )
    is_read_badge.short_description = 'Status'
    
    def rendered_message(self, obj):
        """Display the message content"""
        return obj.message
    rendered_message.short_description = 'Message Preview'
    
    def mark_as_read(self, request, queryset):
        """Bulk action to mark notifications as read"""
        count = 0
        for notification in queryset:
            notification.mark_as_read()
            count += 1
        self.message_user(
            request,
            f'{count} notification(s) marked as read.'
        )
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        """Bulk action to mark notifications as unread"""
        count = 0
        for notification in queryset:
            notification.mark_as_unread()
            count += 1
        self.message_user(
            request,
            f'{count} notification(s) marked as unread.'
        )
    mark_as_unread.short_description = 'Mark selected as unread'
    
    def soft_delete(self, request, queryset):
        """Bulk action to soft delete notifications"""
        count = 0
        for notification in queryset:
            notification.delete_notification()
            count += 1
        self.message_user(
            request,
            f'{count} notification(s) deleted.'
        )
    soft_delete.short_description = 'Delete selected notifications'
    
    def restore(self, request, queryset):
        """Bulk action to restore deleted notifications"""
        count = 0
        for notification in queryset:
            notification.restore_notification()
            count += 1
        self.message_user(
            request,
            f'{count} notification(s) restored.'
        )
    restore.short_description = 'Restore deleted notifications'
    
    def get_queryset(self, request):
        """Only show non-deleted notifications by default"""
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email_frequency',
        'app_notifications_enabled',
        'quiet_hours_enabled',
        'updated_at',
    ]
    
    list_filter = [
        'email_frequency',
        'app_notifications_enabled',
        'quiet_hours_enabled',
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Email Notifications', {
            'fields': (
                'email_on_project_approved',
                'email_on_project_rejected',
                'email_on_submission_review',
                'email_on_comment',
                'email_on_mention',
                'email_frequency',
            ),
            'description': 'Configure when emails should be sent to this user.',
        }),
        ('In-App Notifications', {
            'fields': ('app_notifications_enabled',),
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_enabled',
                'quiet_hours_start',
                'quiet_hours_end',
            ),
            'description': 'Disable notifications during specific hours.',
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    date_hierarchy = 'created_at'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'notification',
        'delivery_method_badge',
        'status_badge',
        'created_at',
    ]
    
    list_filter = [
        'delivery_method',
        'status',
        'created_at',
    ]
    
    search_fields = [
        'notification__title',
        'notification__recipient__username',
    ]
    
    readonly_fields = [
        'created_at',
        'sent_at',
        'notification_link',
    ]
    
    fieldsets = (
        ('Notification', {
            'fields': ('notification', 'notification_link'),
        }),
        ('Delivery', {
            'fields': (
                'delivery_method',
                'status',
                'error_message',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',),
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def delivery_method_badge(self, obj):
        """Display delivery method as a badge"""
        colors = {
            'email': '#0066cc',
            'in_app': '#00cc44',
            'push': '#ff9900',
        }
        color = colors.get(obj.delivery_method, '#cccccc')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_delivery_method_display()
        )
    delivery_method_badge.short_description = 'Method'
    
    def status_badge(self, obj):
        """Display status as a badge"""
        colors = {
            'pending': '#ffaa00',
            'sent': '#00cc44',
            'failed': '#ff3333',
        }
        color = colors.get(obj.status, '#cccccc')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def notification_link(self, obj):
        """Link to the related notification"""
        url = reverse(
            'admin:notification_notification_change',
            args=[obj.notification.pk]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.notification.title
        )
    notification_link.short_description = 'Notification'
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of logs"""
        return False
