"""Task URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubtaskViewSet, TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"subtasks", SubtaskViewSet, basename="subtask")

urlpatterns = [
    path("", include(router.urls)),
]
