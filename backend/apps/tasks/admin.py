"""Admin configuration for tasks."""

from django.contrib import admin

from .models import Subtask, Task, TaskAttachment, TaskComment, TaskHistory


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 0


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    raw_id_fields = ["author"]


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    raw_id_fields = ["uploaded_by"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "task_key",
        "title",
        "task_type",
        "priority",
        "assignee",
        "column",
        "sprint",
        "story_points",
        "created_at",
    ]
    list_filter = ["task_type", "priority", "project", "created_at"]
    search_fields = ["title", "description"]
    raw_id_fields = ["project", "assignee", "reporter", "column", "sprint", "parent"]
    inlines = [SubtaskInline, TaskCommentInline, TaskAttachmentInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author", "content", "created_at"]
    raw_id_fields = ["task", "author"]


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ["filename", "task", "uploaded_by", "file_size", "created_at"]
    raw_id_fields = ["task", "uploaded_by"]


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ["task", "user", "change_type", "field_name", "created_at"]
    list_filter = ["change_type", "created_at"]
    raw_id_fields = ["task", "user"]
