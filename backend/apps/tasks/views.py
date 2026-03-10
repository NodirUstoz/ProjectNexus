"""
Task views: CRUD, move, comments, attachments, subtasks.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.projects.models import BoardColumn

from .models import Subtask, Task, TaskAttachment, TaskComment, TaskHistory
from .serializers import (
    SubtaskSerializer,
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskHistorySerializer,
    TaskListSerializer,
    TaskMoveSerializer,
    TaskUpdateSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for task CRUD and related operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(
            project__workspace__workspace_members__user=self.request.user,
            is_archived=False,
        ).select_related(
            "project", "assignee", "reporter", "column", "sprint"
        ).prefetch_related(
            "labels", "checklist_items", "comments", "attachments"
        ).distinct()

        # Filter by project
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filter by sprint
        sprint_id = self.request.query_params.get("sprint")
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)

        # Filter by column
        column_id = self.request.query_params.get("column")
        if column_id:
            queryset = queryset.filter(column_id=column_id)

        # Filter by assignee
        assignee_id = self.request.query_params.get("assignee")
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)

        # Filter by priority
        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by task type
        task_type = self.request.query_params.get("type")
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        # Filter backlog items (no sprint assigned)
        backlog = self.request.query_params.get("backlog")
        if backlog and backlog.lower() == "true":
            queryset = queryset.filter(sprint__isnull=True)

        # Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        if self.action in ["update", "partial_update"]:
            return TaskUpdateSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskListSerializer

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """Move a task to a different column and/or position."""
        task = self.get_object()
        serializer = TaskMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        column_id = serializer.validated_data["column_id"]
        new_position = serializer.validated_data["position"]

        try:
            new_column = BoardColumn.objects.get(id=column_id)
        except BoardColumn.DoesNotExist:
            return Response(
                {"detail": "Column not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_column = task.column
        old_position = task.position

        # Update positions in old column
        if old_column and old_column != new_column:
            Task.objects.filter(
                column=old_column, position__gt=old_position
            ).update(position=models.F("position") - 1)

        # Update positions in new column
        if old_column != new_column or old_position != new_position:
            Task.objects.filter(
                column=new_column, position__gte=new_position
            ).exclude(id=task.id).update(position=models.F("position") + 1)

        task.column = new_column
        task.position = new_position

        # Mark completed if moved to done column
        if new_column.is_done_column and not task.completed_at:
            task.completed_at = timezone.now()
        elif not new_column.is_done_column and task.completed_at:
            task.completed_at = None

        task.save()

        # Record history
        TaskHistory.objects.create(
            task=task,
            user=request.user,
            change_type=TaskHistory.ChangeType.MOVED,
            field_name="column",
            old_value=str(old_column.name) if old_column else "",
            new_value=new_column.name,
        )

        return Response(TaskListSerializer(task).data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        """List or add comments on a task."""
        task = self.get_object()

        if request.method == "GET":
            comments = task.comments.select_related("author").all()
            serializer = TaskCommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = TaskCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(task=task, author=request.user)

        TaskHistory.objects.create(
            task=task,
            user=request.user,
            change_type=TaskHistory.ChangeType.COMMENTED,
            new_value=comment.content[:200],
        )

        return Response(
            TaskCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get", "post"],
        parser_classes=[MultiPartParser, FormParser],
    )
    def attachments(self, request, pk=None):
        """List or add attachments on a task."""
        task = self.get_object()

        if request.method == "GET":
            attachments = task.attachments.select_related("uploaded_by").all()
            serializer = TaskAttachmentSerializer(
                attachments, many=True, context={"request": request}
            )
            return Response(serializer.data)

        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attachment = TaskAttachment.objects.create(
            task=task,
            uploaded_by=request.user,
            file=file_obj,
            filename=file_obj.name,
            file_size=file_obj.size,
            content_type=file_obj.content_type or "application/octet-stream",
        )

        TaskHistory.objects.create(
            task=task,
            user=request.user,
            change_type=TaskHistory.ChangeType.ATTACHMENT,
            new_value=attachment.filename,
        )

        return Response(
            TaskAttachmentSerializer(attachment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get", "post"])
    def subtasks(self, request, pk=None):
        """List or add subtasks (checklist items) on a task."""
        task = self.get_object()

        if request.method == "GET":
            subtasks = task.checklist_items.all()
            serializer = SubtaskSerializer(subtasks, many=True)
            return Response(serializer.data)

        serializer = SubtaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        max_pos = task.checklist_items.count()
        serializer.save(task=task, position=max_pos)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """Get full history for a task."""
        task = self.get_object()
        history = task.history.select_related("user").all()
        serializer = TaskHistorySerializer(history, many=True)
        return Response(serializer.data)


class SubtaskViewSet(viewsets.ModelViewSet):
    """ViewSet for subtask operations."""

    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subtask.objects.filter(
            task__project__workspace__workspace_members__user=self.request.user
        ).distinct()

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle subtask completion status."""
        subtask = self.get_object()
        subtask.is_completed = not subtask.is_completed
        subtask.save(update_fields=["is_completed"])
        return Response(SubtaskSerializer(subtask).data)


# Import models.F for the move action
from django.db import models  # noqa: E402
