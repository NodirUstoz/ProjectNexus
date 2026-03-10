"""
Time tracking serializers for time entries and timers.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import TimeEntry, Timer


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for time entries."""

    user = UserSerializer(read_only=True)
    task_key = serializers.CharField(source="task.task_key", read_only=True)
    project_name = serializers.CharField(source="task.project.name", read_only=True)

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "task",
            "task_key",
            "project_name",
            "user",
            "description",
            "hours",
            "date",
            "started_at",
            "ended_at",
            "is_billable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a time entry."""

    class Meta:
        model = TimeEntry
        fields = ["task", "description", "hours", "date", "is_billable"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return TimeEntry.objects.create(**validated_data)


class TimerSerializer(serializers.ModelSerializer):
    """Serializer for active timers."""

    user = UserSerializer(read_only=True)
    task_key = serializers.CharField(source="task.task_key", read_only=True)
    project_name = serializers.CharField(source="task.project.name", read_only=True)
    elapsed_seconds = serializers.ReadOnlyField()
    elapsed_hours = serializers.ReadOnlyField()

    class Meta:
        model = Timer
        fields = [
            "id",
            "task",
            "task_key",
            "project_name",
            "user",
            "started_at",
            "description",
            "is_billable",
            "elapsed_seconds",
            "elapsed_hours",
        ]
        read_only_fields = ["id", "user", "started_at"]


class TimerStartSerializer(serializers.Serializer):
    """Serializer for starting a timer."""

    task_id = serializers.UUIDField()
    description = serializers.CharField(required=False, default="")
    is_billable = serializers.BooleanField(required=False, default=True)


class TimeReportFilterSerializer(serializers.Serializer):
    """Serializer for time report query parameters."""

    project_id = serializers.UUIDField(required=False)
    user_id = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    billable_only = serializers.BooleanField(required=False, default=False)
