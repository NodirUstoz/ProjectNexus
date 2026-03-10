"""
Notification views: list, mark read, preferences.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, NotificationPreference
from .serializers import (
    BulkMarkReadSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification listing and management."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related("sender", "content_type")

        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        notification_type = self.request.query_params.get("type")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.mark_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all or selected notifications as read."""
        serializer = BulkMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data.get("notification_ids")

        queryset = Notification.objects.filter(
            recipient=request.user, is_read=False
        )
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)

        count = queryset.update(is_read=True, read_at=timezone.now())
        return Response({"detail": f"{count} notifications marked as read."})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get the count of unread notifications."""
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"unread_count": count})

    @action(detail=False, methods=["delete"])
    def clear_read(self, request):
        """Delete all read notifications older than 30 days."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=30)
        deleted, _ = Notification.objects.filter(
            recipient=request.user,
            is_read=True,
            created_at__lt=cutoff,
        ).delete()
        return Response({"detail": f"{deleted} old notifications cleared."})


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """ViewSet for managing notification preferences."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get the current user's notification preferences."""
        prefs, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(prefs)
        return Response(serializer.data)

    def create(self, request):
        """Update the current user's notification preferences."""
        prefs, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(
            prefs, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
