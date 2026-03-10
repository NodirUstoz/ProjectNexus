"""
Notification serializers for in-app notifications and preferences.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    sender = UserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "notification_type",
            "title",
            "message",
            "target_type",
            "object_id",
            "action_url",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "notification_type",
            "title",
            "message",
            "created_at",
        ]

    def get_target_type(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = [
            "task_assigned",
            "task_updated",
            "task_commented",
            "mentioned",
            "milestone_due",
            "sprint_updates",
            "document_updated",
            "team_updates",
            "daily_digest",
            "weekly_summary",
        ]


class BulkMarkReadSerializer(serializers.Serializer):
    """Serializer for marking multiple notifications as read."""

    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific IDs to mark read. If empty, marks all as read.",
    )
