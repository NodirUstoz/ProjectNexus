"""
Comment models: Comment, CommentReaction.
Generic threaded commenting system that works across tasks, documents, and milestones.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Comment(models.Model):
    """
    Generic comment model using Django's contenttypes framework.
    Supports threading via parent, and can attach to any model (Task, Document, Milestone).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic relation to the target object
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="comments"
    )
    object_id = models.UUIDField()
    target = GenericForeignKey("content_type", "object_id")

    # Comment data
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    # Mentions (stored as JSON list of user IDs)
    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_in_comments",
    )

    is_edited = models.BooleanField(default=False)
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether this comment thread is resolved",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.email} on {self.content_type.model}"

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def reaction_summary(self):
        """Get a summary of reactions on this comment."""
        reactions = self.reactions.values("emoji").annotate(
            count=models.Count("id")
        ).order_by("-count")
        return {r["emoji"]: r["count"] for r in reactions}


class CommentReaction(models.Model):
    """Emoji reactions on comments."""

    REACTION_CHOICES = [
        ("thumbsup", "Thumbs Up"),
        ("thumbsdown", "Thumbs Down"),
        ("heart", "Heart"),
        ("hooray", "Hooray"),
        ("confused", "Confused"),
        ("eyes", "Eyes"),
        ("rocket", "Rocket"),
        ("laugh", "Laugh"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_reactions",
    )
    emoji = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment_reactions"
        unique_together = ("comment", "user", "emoji")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} reacted {self.emoji} on comment"
