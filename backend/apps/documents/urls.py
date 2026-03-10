"""Document URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentFolderViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"folders", DocumentFolderViewSet, basename="folder")

urlpatterns = [
    path("", include(router.urls)),
]
