"""Admin configuration for sprints."""

from django.contrib import admin

from .models import Sprint, SprintGoal


class SprintGoalInline(admin.TabularInline):
    model = SprintGoal
    extra = 0


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "project",
        "sprint_number",
        "status",
        "start_date",
        "end_date",
        "velocity",
        "created_at",
    ]
    list_filter = ["status", "project", "created_at"]
    search_fields = ["name", "goal"]
    raw_id_fields = ["project", "created_by"]
    inlines = [SprintGoalInline]
    date_hierarchy = "start_date"
