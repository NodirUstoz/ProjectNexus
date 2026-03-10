"""Admin configuration for time tracking."""

from django.contrib import admin

from .models import TimeEntry, Timer


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = [
        "task",
        "user",
        "hours",
        "date",
        "is_billable",
        "created_at",
    ]
    list_filter = ["is_billable", "date", "created_at"]
    search_fields = ["description", "task__title"]
    raw_id_fields = ["task", "user"]
    date_hierarchy = "date"


@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    list_display = ["user", "task", "started_at", "elapsed_hours"]
    raw_id_fields = ["user", "task"]
