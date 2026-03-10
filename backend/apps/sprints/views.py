"""
Sprint views: CRUD and sprint lifecycle management.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Sprint, SprintGoal
from .serializers import (
    SprintCreateSerializer,
    SprintDetailSerializer,
    SprintGoalSerializer,
    SprintListSerializer,
)


class SprintViewSet(viewsets.ModelViewSet):
    """ViewSet for sprint CRUD and lifecycle operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Sprint.objects.filter(
            project__workspace__workspace_members__user=self.request.user
        ).select_related("project", "created_by").distinct()

        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return SprintCreateSerializer
        if self.action == "retrieve":
            return SprintDetailSerializer
        return SprintListSerializer

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Start a sprint. Only one sprint per project can be active."""
        sprint = self.get_object()

        if sprint.status != Sprint.Status.PLANNING:
            return Response(
                {"detail": "Only sprints in planning status can be started."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if there's already an active sprint in this project
        active_sprint = Sprint.objects.filter(
            project=sprint.project, status=Sprint.Status.ACTIVE
        ).first()

        if active_sprint:
            return Response(
                {
                    "detail": f"Sprint '{active_sprint.name}' is already active. "
                    "Complete or cancel it before starting a new one."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        sprint.status = Sprint.Status.ACTIVE
        sprint.started_at = timezone.now()
        if not sprint.start_date:
            sprint.start_date = timezone.now().date()
        sprint.save()

        return Response(SprintDetailSerializer(sprint).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Complete a sprint.
        Optionally move incomplete tasks to the next sprint or backlog.
        """
        sprint = self.get_object()

        if sprint.status != Sprint.Status.ACTIVE:
            return Response(
                {"detail": "Only active sprints can be completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        move_to = request.data.get("move_incomplete_to")  # 'backlog' or sprint_id
        incomplete_tasks = sprint.tasks.exclude(column__is_done_column=True)

        if move_to == "backlog":
            incomplete_tasks.update(sprint=None)
        elif move_to:
            try:
                next_sprint = Sprint.objects.get(
                    id=move_to, project=sprint.project
                )
                incomplete_tasks.update(sprint=next_sprint)
            except Sprint.DoesNotExist:
                return Response(
                    {"detail": "Target sprint not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        sprint.status = Sprint.Status.COMPLETED
        sprint.completed_at = timezone.now()
        sprint.velocity = sprint.completed_story_points
        if not sprint.end_date:
            sprint.end_date = timezone.now().date()
        sprint.save()

        return Response(SprintDetailSerializer(sprint).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a sprint and move all tasks back to backlog."""
        sprint = self.get_object()

        if sprint.status == Sprint.Status.COMPLETED:
            return Response(
                {"detail": "Completed sprints cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sprint.tasks.update(sprint=None)
        sprint.status = Sprint.Status.CANCELLED
        sprint.save()

        return Response(SprintDetailSerializer(sprint).data)

    @action(detail=True, methods=["get", "post"])
    def goals(self, request, pk=None):
        """List or add goals for a sprint."""
        sprint = self.get_object()

        if request.method == "GET":
            goals = sprint.goals.all()
            serializer = SprintGoalSerializer(goals, many=True)
            return Response(serializer.data)

        serializer = SprintGoalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sprint=sprint)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="goals/(?P<goal_id>[^/.]+)/toggle")
    def toggle_goal(self, request, pk=None, goal_id=None):
        """Toggle a sprint goal's achieved status."""
        sprint = self.get_object()
        try:
            goal = sprint.goals.get(id=goal_id)
        except SprintGoal.DoesNotExist:
            return Response(
                {"detail": "Goal not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        goal.is_achieved = not goal.is_achieved
        goal.save(update_fields=["is_achieved"])
        return Response(SprintGoalSerializer(goal).data)

    @action(detail=True, methods=["post"])
    def add_tasks(self, request, pk=None):
        """Add tasks to a sprint."""
        sprint = self.get_object()
        task_ids = request.data.get("task_ids", [])

        if not task_ids:
            return Response(
                {"detail": "No task IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.tasks.models import Task

        updated = Task.objects.filter(
            id__in=task_ids, project=sprint.project
        ).update(sprint=sprint)

        return Response(
            {"detail": f"{updated} tasks added to sprint."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_tasks(self, request, pk=None):
        """Remove tasks from a sprint (move to backlog)."""
        sprint = self.get_object()
        task_ids = request.data.get("task_ids", [])

        if not task_ids:
            return Response(
                {"detail": "No task IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.tasks.models import Task

        updated = Task.objects.filter(
            id__in=task_ids, sprint=sprint
        ).update(sprint=None)

        return Response(
            {"detail": f"{updated} tasks removed from sprint."},
            status=status.HTTP_200_OK,
        )
