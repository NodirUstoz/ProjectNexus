"""Project URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BoardColumnViewSet, BoardViewSet, LabelViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"columns", BoardColumnViewSet, basename="column")
router.register(r"labels", LabelViewSet, basename="label")

urlpatterns = [
    path("", include(router.urls)),
]
