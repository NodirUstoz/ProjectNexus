"""Sprint URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SprintViewSet

router = DefaultRouter()
router.register(r"sprints", SprintViewSet, basename="sprint")

urlpatterns = [
    path("", include(router.urls)),
]
