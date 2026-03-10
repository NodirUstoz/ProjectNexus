"""
Sprint serializers for CRUD and sprint lifecycle management.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Sprint, SprintGoal


class SprintGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SprintGoal
        fields = ["id", "title", "description", "is_achieved", "created_at"]
        read_only_fields = ["id", "created_at"]


class SprintListSerializer(serializers.ModelSerializer):
    """Compact serializer for sprint listings."""

    created_by = UserSerializer(read_only=True)
    total_story_points = serializers.ReadOnlyField()
    completed_story_points = serializers.ReadOnlyField()
    task_count = serializers.ReadOnlyField()
    completed_task_count = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Sprint
        fields = [
            "id",
            "name",
            "sprint_number",
            "status",
            "goal",
            "start_date",
            "end_date",
            "started_at",
            "completed_at",
            "created_by",
            "velocity",
            "total_story_points",
            "completed_story_points",
            "task_count",
            "completed_task_count",
            "duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "started_at",
            "completed_at",
            "velocity",
            "created_at",
            "updated_at",
        ]


class SprintDetailSerializer(SprintListSerializer):
    """Full serializer for sprint detail with goals."""

    goals = SprintGoalSerializer(many=True, read_only=True)

    class Meta(SprintListSerializer.Meta):
        fields = SprintListSerializer.Meta.fields + ["goals"]


class SprintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new sprint."""

    class Meta:
        model = Sprint
        fields = ["name", "goal", "start_date", "end_date"]

    def create(self, validated_data):
        project_id = self.context["view"].kwargs.get("project_id")
        if not project_id:
            project_id = self.context["request"].data.get("project_id")

        from apps.projects.models import Project

        project = Project.objects.get(id=project_id)

        # Auto-increment sprint number
        last_sprint = Sprint.objects.filter(project=project).order_by(
            "-sprint_number"
        ).first()
        sprint_number = (last_sprint.sprint_number + 1) if last_sprint else 1

        validated_data["project"] = project
        validated_data["sprint_number"] = sprint_number
        validated_data["created_by"] = self.context["request"].user

        return Sprint.objects.create(**validated_data)
