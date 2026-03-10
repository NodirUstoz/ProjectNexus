"""
Milestone serializers for CRUD operations and progress tracking.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.tasks.serializers import TaskListSerializer

from .models import Milestone, MilestoneTask


class MilestoneTaskSerializer(serializers.ModelSerializer):
    """Serializer for milestone-task links with nested task data."""

    task = TaskListSerializer(read_only=True)

    class Meta:
        model = MilestoneTask
        fields = ["id", "task", "added_at"]
        read_only_fields = ["id", "added_at"]


class MilestoneListSerializer(serializers.ModelSerializer):
    """Compact serializer for milestone listings."""

    owner = UserSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Milestone
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "owner",
            "start_date",
            "due_date",
            "completed_at",
            "color",
            "position",
            "progress_percentage",
            "total_tasks",
            "completed_tasks",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "completed_at", "created_at", "updated_at"]


class MilestoneDetailSerializer(MilestoneListSerializer):
    """Full serializer for milestone detail view with linked tasks."""

    tasks = MilestoneTaskSerializer(source="milestone_tasks", many=True, read_only=True)

    class Meta(MilestoneListSerializer.Meta):
        fields = MilestoneListSerializer.Meta.fields + ["tasks"]


class MilestoneCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new milestone."""

    class Meta:
        model = Milestone
        fields = [
            "title",
            "description",
            "priority",
            "owner",
            "start_date",
            "due_date",
            "color",
        ]

    def create(self, validated_data):
        project_id = self.context["view"].kwargs.get("project_id")
        if not project_id:
            project_id = self.context["request"].data.get("project_id")

        from apps.projects.models import Project

        project = Project.objects.get(id=project_id)
        validated_data["project"] = project

        max_position = Milestone.objects.filter(project=project).count()
        validated_data["position"] = max_position

        return Milestone.objects.create(**validated_data)


class AddTaskToMilestoneSerializer(serializers.Serializer):
    """Serializer for linking tasks to a milestone."""

    task_ids = serializers.ListField(
        child=serializers.UUIDField(), min_length=1
    )
