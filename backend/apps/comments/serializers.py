"""
Comment serializers for the generic commenting system.
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Comment, CommentReaction


class CommentReactionSerializer(serializers.ModelSerializer):
    """Serializer for comment reactions."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentReaction
        fields = ["id", "user", "emoji", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with nested replies and reactions."""

    author = UserSerializer(read_only=True)
    reply_count = serializers.ReadOnlyField()
    reaction_summary = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "body",
            "parent",
            "is_edited",
            "is_resolved",
            "reply_count",
            "reaction_summary",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "is_edited",
            "created_at",
            "updated_at",
        ]

    def get_replies(self, obj):
        """Get first-level replies for this comment."""
        if obj.parent is not None:
            return []
        replies = obj.replies.select_related("author").all()[:10]
        return CommentSerializer(replies, many=True).data


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment on any target object."""

    target_type = serializers.ChoiceField(
        choices=["task", "document", "milestone"],
        help_text="The type of object to comment on",
    )
    target_id = serializers.UUIDField(
        help_text="The UUID of the target object",
    )
    body = serializers.CharField()
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    mentioned_user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=[],
    )

    def validate_target_type(self, value):
        model_map = {
            "task": "tasks.task",
            "document": "documents.document",
            "milestone": "milestones.milestone",
        }
        app_label, model_name = model_map[value].split(".")
        try:
            ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(
                f"Content type for {value} not found."
            )
        return value

    def create(self, validated_data):
        model_map = {
            "task": ("tasks", "task"),
            "document": ("documents", "document"),
            "milestone": ("milestones", "milestone"),
        }
        target_type = validated_data["target_type"]
        app_label, model_name = model_map[target_type]
        content_type = ContentType.objects.get(
            app_label=app_label, model=model_name
        )

        parent = None
        parent_id = validated_data.get("parent_id")
        if parent_id:
            parent = Comment.objects.get(id=parent_id)

        mentioned_ids = validated_data.get("mentioned_user_ids", [])

        comment = Comment.objects.create(
            content_type=content_type,
            object_id=validated_data["target_id"],
            author=self.context["request"].user,
            body=validated_data["body"],
            parent=parent,
        )

        if mentioned_ids:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(id__in=mentioned_ids)
            comment.mentioned_users.set(users)

        return comment


class ToggleReactionSerializer(serializers.Serializer):
    """Serializer for adding or removing a reaction on a comment."""

    emoji = serializers.ChoiceField(
        choices=[c[0] for c in CommentReaction.REACTION_CHOICES]
    )
