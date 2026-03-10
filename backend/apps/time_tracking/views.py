"""
Time tracking views: time entries, timers, and time reports.
"""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tasks.models import Task

from .models import TimeEntry, Timer
from .serializers import (
    TimeEntryCreateSerializer,
    TimeEntrySerializer,
    TimerSerializer,
    TimerStartSerializer,
)


class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for time entry CRUD operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TimeEntry.objects.filter(
            task__project__workspace__workspace_members__user=self.request.user
        ).select_related("task", "task__project", "user").distinct()

        # Filter by task
        task_id = self.request.query_params.get("task")
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        # Filter by project
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(task__project_id=project_id)

        # Filter by user
        user_id = self.request.query_params.get("user")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Filter billable only
        billable = self.request.query_params.get("billable")
        if billable and billable.lower() == "true":
            queryset = queryset.filter(is_billable=True)

        # My entries only
        mine = self.request.query_params.get("mine")
        if mine and mine.lower() == "true":
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return TimeEntryCreateSerializer
        return TimeEntrySerializer

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get time summary for the current user over a period."""
        days = int(request.query_params.get("days", 7))
        start_date = timezone.now().date() - timedelta(days=days)

        entries = TimeEntry.objects.filter(
            user=request.user,
            date__gte=start_date,
        )

        total_hours = entries.aggregate(total=Sum("hours"))["total"] or 0
        billable_hours = entries.filter(is_billable=True).aggregate(
            total=Sum("hours")
        )["total"] or 0

        # Group by date
        daily_breakdown = {}
        for entry in entries:
            date_str = entry.date.isoformat()
            if date_str not in daily_breakdown:
                daily_breakdown[date_str] = {"hours": 0, "entries": 0}
            daily_breakdown[date_str]["hours"] += float(entry.hours)
            daily_breakdown[date_str]["entries"] += 1

        return Response({
            "period_days": days,
            "total_hours": float(total_hours),
            "billable_hours": float(billable_hours),
            "non_billable_hours": float(total_hours - billable_hours),
            "daily_average": round(float(total_hours) / max(days, 1), 2),
            "daily_breakdown": daily_breakdown,
        })

    @action(detail=False, methods=["get"])
    def report(self, request):
        """Generate a time report grouped by project and user."""
        project_id = request.query_params.get("project")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = TimeEntry.objects.filter(
            task__project__workspace__workspace_members__user=request.user
        ).select_related("task__project", "user")

        if project_id:
            queryset = queryset.filter(task__project_id=project_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Group by project
        project_data = {}
        for entry in queryset:
            proj_key = str(entry.task.project.id)
            if proj_key not in project_data:
                project_data[proj_key] = {
                    "project_name": entry.task.project.name,
                    "project_key": entry.task.project.key,
                    "total_hours": 0,
                    "billable_hours": 0,
                    "entries_count": 0,
                    "members": {},
                }
            project_data[proj_key]["total_hours"] += float(entry.hours)
            project_data[proj_key]["entries_count"] += 1
            if entry.is_billable:
                project_data[proj_key]["billable_hours"] += float(entry.hours)

            user_key = str(entry.user.id)
            if user_key not in project_data[proj_key]["members"]:
                project_data[proj_key]["members"][user_key] = {
                    "name": entry.user.full_name,
                    "email": entry.user.email,
                    "hours": 0,
                }
            project_data[proj_key]["members"][user_key]["hours"] += float(entry.hours)

        # Convert members dict to list for cleaner output
        for proj in project_data.values():
            proj["members"] = list(proj["members"].values())

        return Response(list(project_data.values()))


class TimerViewSet(viewsets.ViewSet):
    """ViewSet for managing active timers."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """List all active timers for the current user."""
        timers = Timer.objects.filter(
            user=request.user
        ).select_related("task", "task__project")
        serializer = TimerSerializer(timers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def start(self, request):
        """Start a new timer on a task."""
        serializer = TimerStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Stop any existing timer for this user
        existing = Timer.objects.filter(user=request.user)
        for timer in existing:
            timer.stop_and_create_entry()

        timer = Timer.objects.create(
            task=task,
            user=request.user,
            description=serializer.validated_data.get("description", ""),
            is_billable=serializer.validated_data.get("is_billable", True),
        )

        return Response(
            TimerSerializer(timer).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def stop(self, request):
        """Stop the current active timer and create a time entry."""
        timer = Timer.objects.filter(user=request.user).first()
        if not timer:
            return Response(
                {"detail": "No active timer found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        entry = timer.stop_and_create_entry()
        return Response(TimeEntrySerializer(entry).data)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get the current active timer for the user."""
        timer = Timer.objects.filter(
            user=request.user
        ).select_related("task", "task__project").first()

        if not timer:
            return Response(
                {"detail": "No active timer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(TimerSerializer(timer).data)

    @action(detail=False, methods=["post"])
    def discard(self, request):
        """Discard the current timer without creating a time entry."""
        deleted, _ = Timer.objects.filter(user=request.user).delete()
        if deleted == 0:
            return Response(
                {"detail": "No active timer found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"detail": "Timer discarded."})
