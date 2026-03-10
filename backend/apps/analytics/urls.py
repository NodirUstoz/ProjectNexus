"""Analytics URL configuration."""

from django.urls import path

from .views import (
    ActivityFeedView,
    BurndownChartView,
    ProjectDashboardView,
    SprintVelocityView,
)

urlpatterns = [
    path(
        "projects/<uuid:project_id>/dashboard/",
        ProjectDashboardView.as_view(),
        name="project-dashboard",
    ),
    path(
        "projects/<uuid:project_id>/velocity/",
        SprintVelocityView.as_view(),
        name="sprint-velocity",
    ),
    path(
        "sprints/<uuid:sprint_id>/burndown/",
        BurndownChartView.as_view(),
        name="burndown-chart",
    ),
    path(
        "activity/",
        ActivityFeedView.as_view(),
        name="activity-feed",
    ),
]
