"""
Analytics views: project dashboards, sprint velocity, burndown charts,
team performance, and activity feeds.
"""

from collections import defaultdict
from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.sprints.models import Sprint
from apps.tasks.models import Task, TaskHistory
from apps.time_tracking.models import TimeEntry


class ProjectDashboardView(APIView):
    """Overview analytics for a single project."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                id=project_id,
                workspace__workspace_members__user=request.user,
            )
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        tasks = Task.objects.filter(project=project, is_archived=False)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(column__is_done_column=True).count()

        # Task distribution by type
        type_distribution = dict(
            tasks.values_list("task_type").annotate(count=Count("id")).order_by()
        )

        # Task distribution by priority
        priority_distribution = dict(
            tasks.values_list("priority").annotate(count=Count("id")).order_by()
        )

        # Tasks by assignee
        tasks_by_assignee = list(
            tasks.filter(assignee__isnull=False)
            .values("assignee__email", "assignee__first_name", "assignee__last_name")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(column__is_done_column=True)),
            )
            .order_by("-total")[:10]
        )

        # Overdue tasks
        overdue_count = tasks.filter(
            due_date__lt=timezone.now().date(),
            completed_at__isnull=True,
        ).count()

        # Story points
        total_points = tasks.aggregate(total=Sum("story_points"))["total"] or 0
        completed_points = tasks.filter(
            column__is_done_column=True
        ).aggregate(total=Sum("story_points"))["total"] or 0

        # Time tracking summary
        total_estimated = tasks.aggregate(
            total=Sum("original_estimate_hours")
        )["total"] or 0
        total_logged = tasks.aggregate(
            total=Sum("time_spent_hours")
        )["total"] or 0

        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_created = tasks.filter(created_at__gte=week_ago).count()
        recent_completed = tasks.filter(completed_at__gte=week_ago).count()

        return Response({
            "project": {
                "id": str(project.id),
                "name": project.name,
                "key": project.key,
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": tasks.filter(
                    column__is_done_column=False, column__isnull=False
                ).exclude(column__name="Backlog").count(),
                "overdue": overdue_count,
                "unassigned": tasks.filter(assignee__isnull=True).count(),
                "completion_rate": round(
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
                ),
            },
            "story_points": {
                "total": total_points,
                "completed": completed_points,
            },
            "time_tracking": {
                "estimated_hours": float(total_estimated),
                "logged_hours": float(total_logged),
            },
            "distribution": {
                "by_type": type_distribution,
                "by_priority": priority_distribution,
                "by_assignee": tasks_by_assignee,
            },
            "recent_activity": {
                "created_this_week": recent_created,
                "completed_this_week": recent_completed,
            },
        })


class SprintVelocityView(APIView):
    """Sprint velocity chart data showing story points completed per sprint."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        sprints = Sprint.objects.filter(
            project_id=project_id,
            status=Sprint.Status.COMPLETED,
            project__workspace__workspace_members__user=request.user,
        ).order_by("sprint_number")[:12]

        velocity_data = []
        for sprint in sprints:
            velocity_data.append({
                "sprint_number": sprint.sprint_number,
                "name": sprint.name,
                "planned_points": sprint.total_story_points,
                "completed_points": sprint.completed_story_points,
                "velocity": sprint.velocity or 0,
                "task_count": sprint.task_count,
                "completed_task_count": sprint.completed_task_count,
                "duration_days": sprint.duration_days,
                "start_date": sprint.start_date.isoformat() if sprint.start_date else None,
                "end_date": sprint.end_date.isoformat() if sprint.end_date else None,
            })

        # Calculate averages
        velocities = [v["velocity"] for v in velocity_data if v["velocity"] > 0]
        avg_velocity = round(sum(velocities) / len(velocities), 1) if velocities else 0

        return Response({
            "velocity_data": velocity_data,
            "average_velocity": avg_velocity,
            "sprint_count": len(velocity_data),
            "trend": self._calculate_trend(velocities),
        })

    def _calculate_trend(self, values):
        """Simple trend calculation: increasing, decreasing, or stable."""
        if len(values) < 3:
            return "insufficient_data"
        recent = sum(values[-3:]) / 3
        earlier = sum(values[:3]) / 3
        if recent > earlier * 1.1:
            return "increasing"
        elif recent < earlier * 0.9:
            return "decreasing"
        return "stable"


class BurndownChartView(APIView):
    """Burndown chart data for a specific sprint."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, sprint_id):
        try:
            sprint = Sprint.objects.get(
                id=sprint_id,
                project__workspace__workspace_members__user=request.user,
            )
        except Sprint.DoesNotExist:
            return Response({"detail": "Sprint not found."}, status=404)

        if not sprint.start_date or not sprint.end_date:
            return Response(
                {"detail": "Sprint dates are not set."},
                status=400,
            )

        total_points = sprint.total_story_points
        tasks = sprint.tasks.all()

        # Build daily burndown data
        burndown = []
        current_date = sprint.start_date
        end = sprint.end_date
        today = timezone.now().date()

        while current_date <= end:
            # Ideal remaining
            total_days = (end - sprint.start_date).days or 1
            elapsed_days = (current_date - sprint.start_date).days
            ideal_remaining = total_points * (1 - elapsed_days / total_days)

            # Actual remaining (only for past dates)
            actual_remaining = None
            if current_date <= today:
                completed_by_date = tasks.filter(
                    completed_at__date__lte=current_date
                ).aggregate(total=Sum("story_points"))["total"] or 0
                actual_remaining = total_points - completed_by_date

            burndown.append({
                "date": current_date.isoformat(),
                "ideal_remaining": round(ideal_remaining, 1),
                "actual_remaining": actual_remaining,
            })
            current_date += timedelta(days=1)

        return Response({
            "sprint": {
                "id": str(sprint.id),
                "name": sprint.name,
                "sprint_number": sprint.sprint_number,
                "total_points": total_points,
            },
            "burndown": burndown,
        })


class ActivityFeedView(APIView):
    """Recent activity feed across all projects in a workspace."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace")
        limit = int(request.query_params.get("limit", 50))
        days = int(request.query_params.get("days", 7))

        since = timezone.now() - timedelta(days=days)

        queryset = TaskHistory.objects.filter(
            task__project__workspace__workspace_members__user=request.user,
            created_at__gte=since,
        ).select_related("task", "task__project", "user")

        if workspace_id:
            queryset = queryset.filter(
                task__project__workspace_id=workspace_id
            )

        activities = queryset.order_by("-created_at")[:limit]

        feed = []
        for activity in activities:
            feed.append({
                "id": str(activity.id),
                "type": activity.change_type,
                "user": {
                    "email": activity.user.email if activity.user else None,
                    "name": activity.user.full_name if activity.user else "System",
                },
                "task": {
                    "id": str(activity.task.id),
                    "key": activity.task.task_key,
                    "title": activity.task.title,
                },
                "project": {
                    "id": str(activity.task.project.id),
                    "name": activity.task.project.name,
                    "key": activity.task.project.key,
                },
                "field": activity.field_name,
                "old_value": activity.old_value,
                "new_value": activity.new_value,
                "timestamp": activity.created_at.isoformat(),
            })

        return Response(feed)
