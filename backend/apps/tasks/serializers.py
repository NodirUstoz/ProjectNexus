"""
Task serializers for CRUD, comments, attachments, and history.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.projects.serializers import LabelSerializer

from .models import Subtask, Task, TaskAttachment, TaskComment, TaskHistory


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ["id", "title", "is_completed", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "author", "content", "edited", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "edited", "created_at", "updated_at"]


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TaskAttachment
        fields = [
            "id",
            "uploaded_by",
            "file",
            "file_url",
            "filename",
            "file_size",
            "content_type",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "filename", "file_size", "content_type", "created_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class TaskHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = [
            "id",
            "user",
            "change_type",
            "field_name",
            "old_value",
            "new_value",
            "created_at",
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Compact serializer for task listings (board view, backlog)."""

    task_key = serializers.ReadOnlyField()
    assignee = UserSerializer(read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    subtask_count = serializers.SerializerMethodField()
    subtask_completed = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "task_key",
            "task_number",
            "title",
            "task_type",
            "priority",
            "assignee",
            "labels",
            "story_points",
            "due_date",
            "column",
            "sprint",
            "position",
            "subtask_count",
            "subtask_completed",
            "comment_count",
            "attachment_count",
            "created_at",
            "updated_at",
        ]

    def get_subtask_count(self, obj):
        return obj.checklist_items.count()

    def get_subtask_completed(self, obj):
        return obj.checklist_items.filter(is_completed=True).count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class TaskDetailSerializer(TaskListSerializer):
    """Full serializer for task detail view."""

    reporter = UserSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    checklist_items = SubtaskSerializer(many=True, read_only=True)
    history = TaskHistorySerializer(many=True, read_only=True)

    class Meta(TaskListSerializer.Meta):
        fields = TaskListSerializer.Meta.fields + [
            "description",
            "reporter",
            "original_estimate_hours",
            "time_spent_hours",
            "start_date",
            "completed_at",
            "comments",
            "attachments",
            "checklist_items",
            "history",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new task."""

    label_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "task_type",
            "priority",
            "assignee",
            "story_points",
            "original_estimate_hours",
            "due_date",
            "start_date",
            "column",
            "sprint",
            "parent",
            "label_ids",
        ]

    def create(self, validated_data):
        label_ids = validated_data.pop("label_ids", [])
        project_id = self.context["view"].kwargs.get("project_id")
        if not project_id:
            project_id = self.context["request"].data.get("project_id")

        from apps.projects.models import Project

        project = Project.objects.get(id=project_id)
        validated_data["project"] = project
        validated_data["reporter"] = self.context["request"].user

        # Set position to end of column
        if validated_data.get("column"):
            max_pos = Task.objects.filter(
                column=validated_data["column"]
            ).count()
            validated_data["position"] = max_pos

        task = Task.objects.create(**validated_data)

        if label_ids:
            task.labels.set(label_ids)

        # Create history entry
        TaskHistory.objects.create(
            task=task,
            user=self.context["request"].user,
            change_type=TaskHistory.ChangeType.CREATED,
            new_value=task.title,
        )

        return task


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a task with change tracking."""

    label_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "task_type",
            "priority",
            "assignee",
            "story_points",
            "original_estimate_hours",
            "due_date",
            "start_date",
            "column",
            "sprint",
            "position",
            "label_ids",
        ]

    def update(self, instance, validated_data):
        label_ids = validated_data.pop("label_ids", None)
        user = self.context["request"].user

        # Track changes for history
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != new_value:
                change_type = TaskHistory.ChangeType.UPDATED
                if field == "column":
                    change_type = TaskHistory.ChangeType.MOVED
                elif field == "assignee":
                    change_type = TaskHistory.ChangeType.ASSIGNED

                TaskHistory.objects.create(
                    task=instance,
                    user=user,
                    change_type=change_type,
                    field_name=field,
                    old_value=str(old_value) if old_value else "",
                    new_value=str(new_value) if new_value else "",
                )

        instance = super().update(instance, validated_data)

        if label_ids is not None:
            instance.labels.set(label_ids)

        return instance


class TaskMoveSerializer(serializers.Serializer):
    """Serializer for moving a task between columns."""

    column_id = serializers.UUIDField()
    position = serializers.IntegerField(min_value=0)
