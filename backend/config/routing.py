"""
WebSocket URL routing for ProjectNexus.
"""

from django.urls import re_path

from apps.notifications.consumers import NotificationConsumer
from apps.tasks.consumers import TaskBoardConsumer

websocket_urlpatterns = [
    re_path(r"ws/tasks/(?P<project_id>\w+)/$", TaskBoardConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
]
