"""
WebSocket consumers for real-time task board updates.
"""

import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.accounts.models import WorkspaceMember

logger = logging.getLogger(__name__)


class TaskBoardConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time task board updates.
    Each project has its own group so all users viewing that project
    receive live updates when tasks are created, updated, moved, or deleted.
    """

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"
        user = self.scope.get("user")

        if not user or user.is_anonymous:
            await self.close()
            return

        # Verify user has access to this project
        has_access = await self.verify_project_access(user, self.project_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(
            f"User {user.email} connected to project board {self.project_id}"
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def receive_json(self, content):
        """Handle incoming WebSocket messages from clients."""
        event_type = content.get("type")
        data = content.get("data", {})

        if event_type == "task.update":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "task_updated",
                    "data": data,
                    "sender_channel": self.channel_name,
                },
            )
        elif event_type == "task.move":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "task_moved",
                    "data": data,
                    "sender_channel": self.channel_name,
                },
            )
        elif event_type == "cursor.move":
            # Broadcast cursor position for collaborative awareness
            user = self.scope.get("user")
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "cursor_moved",
                    "data": {
                        "user_id": str(user.id),
                        "user_name": user.full_name,
                        "position": data.get("position"),
                    },
                    "sender_channel": self.channel_name,
                },
            )

    async def task_created(self, event):
        """Broadcast task creation to all group members."""
        await self.send_json({
            "type": "task.created",
            "data": event["data"],
        })

    async def task_updated(self, event):
        """Broadcast task update to all group members except sender."""
        if self.channel_name != event.get("sender_channel"):
            await self.send_json({
                "type": "task.updated",
                "data": event["data"],
            })

    async def task_moved(self, event):
        """Broadcast task move to all group members except sender."""
        if self.channel_name != event.get("sender_channel"):
            await self.send_json({
                "type": "task.moved",
                "data": event["data"],
            })

    async def task_deleted(self, event):
        """Broadcast task deletion to all group members."""
        await self.send_json({
            "type": "task.deleted",
            "data": event["data"],
        })

    async def comment_added(self, event):
        """Broadcast new comment to all group members."""
        await self.send_json({
            "type": "comment.added",
            "data": event["data"],
        })

    async def cursor_moved(self, event):
        """Broadcast cursor position to all group members except sender."""
        if self.channel_name != event.get("sender_channel"):
            await self.send_json({
                "type": "cursor.moved",
                "data": event["data"],
            })

    @database_sync_to_async
    def verify_project_access(self, user, project_id):
        """Verify the user has access to the project's workspace."""
        from apps.projects.models import Project

        try:
            project = Project.objects.get(id=project_id)
            return WorkspaceMember.objects.filter(
                workspace=project.workspace, user=user
            ).exists()
        except Project.DoesNotExist:
            return False
