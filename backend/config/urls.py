"""ProjectNexus URL Configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.projects.urls")),
    path("api/", include("apps.tasks.urls")),
    path("api/", include("apps.sprints.urls")),
    path("api/", include("apps.milestones.urls")),
    path("api/", include("apps.teams.urls")),
    path("api/", include("apps.time_tracking.urls")),
    path("api/", include("apps.documents.urls")),
    path("api/", include("apps.comments.urls")),
    path("api/", include("apps.notifications.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
