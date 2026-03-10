"""Milestone URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MilestoneViewSet

router = DefaultRouter()
router.register(r"milestones", MilestoneViewSet, basename="milestone")

urlpatterns = [
    path("", include(router.urls)),
]
