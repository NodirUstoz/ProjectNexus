"""
Milestone views: CRUD, task linking, progress tracking.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tasks.models import Task

from .models import Milestone, MilestoneTask
from .serializers import (
    AddTaskToMilestoneSerializer,
    MilestoneCreateSerializer,
    MilestoneDetailSerializer,
    MilestoneListSerializer,
    MilestoneTaskSerializer,
)


class MilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet for milestone CRUD and task management."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Milestone.objects.filter(
            project__workspace__workspace_members__user=self.request.user
        ).select_related("project", "owner").distinct()

        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return MilestoneCreateSerializer
        if self.action == "retrieve":
            return MilestoneDetailSerializer
        return MilestoneListSerializer

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a milestone as completed."""
        milestone = self.get_object()
        milestone.status = Milestone.Status.COMPLETED
        milestone.completed_at = timezone.now()
        milestone.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(MilestoneDetailSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """Reopen a completed or cancelled milestone."""
        milestone = self.get_object()
        if milestone.is_overdue:
            milestone.status = Milestone.Status.OVERDUE
        elif milestone.completed_tasks > 0:
            milestone.status = Milestone.Status.IN_PROGRESS
        else:
            milestone.status = Milestone.Status.NOT_STARTED
        milestone.completed_at = None
        milestone.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(MilestoneDetailSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def add_tasks(self, request, pk=None):
        """Link tasks to this milestone."""
        milestone = self.get_object()
        serializer = AddTaskToMilestoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_ids = serializer.validated_data["task_ids"]
        tasks = Task.objects.filter(
            id__in=task_ids, project=milestone.project
        )

        created_count = 0
        for task in tasks:
            _, created = MilestoneTask.objects.get_or_create(
                milestone=milestone,
                task=task,
                defaults={"added_by": request.user},
            )
            if created:
                created_count += 1

        # Auto-update milestone status
        if milestone.status == Milestone.Status.NOT_STARTED and created_count > 0:
            milestone.status = Milestone.Status.IN_PROGRESS
            milestone.save(update_fields=["status", "updated_at"])

        return Response(
            {"detail": f"{created_count} tasks linked to milestone."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_tasks(self, request, pk=None):
        """Unlink tasks from this milestone."""
        milestone = self.get_object()
        task_ids = request.data.get("task_ids", [])

        deleted_count, _ = MilestoneTask.objects.filter(
            milestone=milestone, task_id__in=task_ids
        ).delete()

        return Response(
            {"detail": f"{deleted_count} tasks removed from milestone."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """List all tasks linked to this milestone."""
        milestone = self.get_object()
        milestone_tasks = milestone.milestone_tasks.select_related(
            "task", "task__assignee", "task__column"
        ).all()
        serializer = MilestoneTaskSerializer(milestone_tasks, many=True)
        return Response(serializer.data)
