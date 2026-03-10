"""
WebSocket consumer for real-time notification delivery.
"""

import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for delivering notifications in real-time.
    Each authenticated user has their own notification channel.
    """

    async def connect(self):
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            await self.close()
            return

        self.user_id = str(user.id)
        self.group_name = f"notifications_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connection
        unread_count = await self.get_unread_count(user)
        await self.send_json({
            "type": "connected",
            "unread_count": unread_count,
        })

        logger.info(f"User {user.email} connected to notifications")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive_json(self, content):
        """Handle incoming messages from the client."""
        event_type = content.get("type")

        if event_type == "mark_read":
            notification_id = content.get("notification_id")
            if notification_id:
                await self.mark_notification_read(notification_id)
                unread_count = await self.get_unread_count(self.scope["user"])
                await self.send_json({
                    "type": "unread_count",
                    "count": unread_count,
                })

        elif event_type == "mark_all_read":
            await self.mark_all_read(self.scope["user"])
            await self.send_json({
                "type": "unread_count",
                "count": 0,
            })

    async def notification_send(self, event):
        """Send a notification to the user's WebSocket."""
        await self.send_json({
            "type": "notification",
            "data": event["data"],
        })

    async def unread_count_update(self, event):
        """Send updated unread count."""
        await self.send_json({
            "type": "unread_count",
            "count": event["count"],
        })

    @database_sync_to_async
    def get_unread_count(self, user):
        from .models import Notification
        return Notification.objects.filter(
            recipient=user, is_read=False
        ).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_read()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_all_read(self, user):
        from django.utils import timezone
        from .models import Notification
        Notification.objects.filter(
            recipient=user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
