"""Time tracking URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TimeEntryViewSet, TimerViewSet

router = DefaultRouter()
router.register(r"time-entries", TimeEntryViewSet, basename="time-entry")
router.register(r"timers", TimerViewSet, basename="timer")

urlpatterns = [
    path("", include(router.urls)),
]
