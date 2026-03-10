"""Admin configuration for milestones."""

from django.contrib import admin

from .models import Milestone, MilestoneTask


class MilestoneTaskInline(admin.TabularInline):
    model = MilestoneTask
    extra = 0
    raw_id_fields = ["task", "added_by"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "project",
        "status",
        "priority",
        "owner",
        "due_date",
        "progress_percentage",
        "created_at",
    ]
    list_filter = ["status", "priority", "due_date", "created_at"]
    search_fields = ["title", "description"]
    raw_id_fields = ["project", "owner"]
    inlines = [MilestoneTaskInline]
    date_hierarchy = "due_date"


@admin.register(MilestoneTask)
class MilestoneTaskAdmin(admin.ModelAdmin):
    list_display = ["milestone", "task", "added_by", "added_at"]
    raw_id_fields = ["milestone", "task", "added_by"]
