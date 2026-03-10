"""
Notification models: Notification, NotificationPreference.
Handles in-app notifications and user preferences for notification delivery.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Notification(models.Model):
    """In-app notification for a user, linked to any object via content types."""

    class NotificationType(models.TextChoices):
        TASK_ASSIGNED = "task_assigned", "Task Assigned"
        TASK_UPDATED = "task_updated", "Task Updated"
        TASK_COMPLETED = "task_completed", "Task Completed"
        TASK_COMMENTED = "task_commented", "Task Commented"
        MENTIONED = "mentioned", "Mentioned"
        MILESTONE_DUE = "milestone_due", "Milestone Due"
        MILESTONE_COMPLETED = "milestone_completed", "Milestone Completed"
        SPRINT_STARTED = "sprint_started", "Sprint Started"
        SPRINT_COMPLETED = "sprint_completed", "Sprint Completed"
        DOCUMENT_UPDATED = "document_updated", "Document Updated"
        TEAM_JOINED = "team_joined", "Team Joined"
        PROJECT_INVITED = "project_invited", "Project Invited"
        WORKSPACE_INVITED = "workspace_invited", "Workspace Invited"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(
        max_length=25, choices=NotificationType.choices
    )
    title = models.CharField(max_length=300)
    message = models.TextField(blank=True)

    # Generic relation to the target object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")

    # URL for deep-linking in the frontend
    action_url = models.CharField(max_length=500, blank=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient.email}"

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])


class NotificationPreference(models.Model):
    """Per-user preferences for notification delivery channels."""

    class Channel(models.TextChoices):
        IN_APP = "in_app", "In-App"
        EMAIL = "email", "Email"
        BOTH = "both", "Both"
        NONE = "none", "None"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    task_assigned = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.BOTH
    )
    task_updated = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.IN_APP
    )
    task_commented = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.BOTH
    )
    mentioned = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.BOTH
    )
    milestone_due = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.BOTH
    )
    sprint_updates = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.IN_APP
    )
    document_updated = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.IN_APP
    )
    team_updates = models.CharField(
        max_length=10, choices=Channel.choices, default=Channel.IN_APP
    )
    daily_digest = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"Preferences for {self.user.email}"
