"""
Comment views: generic comments with threading, reactions, and resolution.
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comment, CommentReaction
from .serializers import (
    CommentCreateSerializer,
    CommentReactionSerializer,
    CommentSerializer,
    ToggleReactionSerializer,
)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for generic comment operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "author", "content_type"
        ).prefetch_related("reactions", "replies").all()

        # Filter by target
        target_type = self.request.query_params.get("target_type")
        target_id = self.request.query_params.get("target_id")

        if target_type and target_id:
            model_map = {
                "task": ("tasks", "task"),
                "document": ("documents", "document"),
                "milestone": ("milestones", "milestone"),
            }
            if target_type in model_map:
                app_label, model_name = model_map[target_type]
                try:
                    ct = ContentType.objects.get(
                        app_label=app_label, model=model_name
                    )
                    queryset = queryset.filter(
                        content_type=ct, object_id=target_id
                    )
                except ContentType.DoesNotExist:
                    queryset = queryset.none()

        # Only show top-level comments by default
        show_all = self.request.query_params.get("all")
        if not show_all:
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        return CommentSerializer

    def perform_update(self, serializer):
        """Mark comment as edited when updated."""
        serializer.save(is_edited=True)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark a comment thread as resolved."""
        comment = self.get_object()
        comment.is_resolved = True
        comment.save(update_fields=["is_resolved", "updated_at"])
        return Response(CommentSerializer(comment).data)

    @action(detail=True, methods=["post"])
    def unresolve(self, request, pk=None):
        """Reopen a resolved comment thread."""
        comment = self.get_object()
        comment.is_resolved = False
        comment.save(update_fields=["is_resolved", "updated_at"])
        return Response(CommentSerializer(comment).data)

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        """Toggle a reaction on a comment."""
        comment = self.get_object()
        serializer = ToggleReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emoji = serializer.validated_data["emoji"]

        existing = CommentReaction.objects.filter(
            comment=comment, user=request.user, emoji=emoji
        ).first()

        if existing:
            existing.delete()
            return Response({"detail": "Reaction removed."})

        reaction = CommentReaction.objects.create(
            comment=comment, user=request.user, emoji=emoji
        )
        return Response(
            CommentReactionSerializer(reaction).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def reactions(self, request, pk=None):
        """List all reactions on a comment."""
        comment = self.get_object()
        reactions = comment.reactions.select_related("user").all()
        serializer = CommentReactionSerializer(reactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def thread(self, request, pk=None):
        """Get full thread for a comment including all nested replies."""
        comment = self.get_object()
        # Get the root comment
        root = comment
        while root.parent is not None:
            root = root.parent

        replies = Comment.objects.filter(
            parent=root
        ).select_related("author").prefetch_related("reactions")

        data = CommentSerializer(root).data
        data["all_replies"] = CommentSerializer(replies, many=True).data
        return Response(data)
