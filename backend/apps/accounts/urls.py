"""Account URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
    WorkspaceViewSet,
)

router = DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspace")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("", include(router.urls)),
]
