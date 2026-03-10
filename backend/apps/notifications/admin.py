"""Admin configuration for notifications."""

from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "recipient",
        "notification_type",
        "title",
        "sender",
        "is_read",
        "created_at",
    ]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["title", "message"]
    raw_id_fields = ["recipient", "sender"]
    date_hierarchy = "created_at"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "task_assigned",
        "mentioned",
        "daily_digest",
        "weekly_summary",
    ]
    raw_id_fields = ["user"]
