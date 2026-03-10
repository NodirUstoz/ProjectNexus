"""Notification URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationPreferenceViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(
    r"notification-preferences",
    NotificationPreferenceViewSet,
    basename="notification-preference",
)

urlpatterns = [
    path("", include(router.urls)),
]
