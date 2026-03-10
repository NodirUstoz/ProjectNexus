"""Admin configuration for projects."""

from django.contrib import admin

from .models import Board, BoardColumn, Label, Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0
    raw_id_fields = ["user"]


class BoardColumnInline(admin.TabularInline):
    model = BoardColumn
    extra = 0
    ordering = ["position"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "workspace", "project_type", "lead", "is_archived", "created_at"]
    list_filter = ["project_type", "is_archived", "created_at"]
    search_fields = ["name", "key"]
    raw_id_fields = ["workspace", "lead"]
    inlines = [ProjectMemberInline]


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "is_default", "created_at"]
    list_filter = ["is_default"]
    raw_id_fields = ["project"]
    inlines = [BoardColumnInline]


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ["name", "board", "position", "wip_limit", "is_done_column"]
    list_filter = ["is_done_column"]
    ordering = ["board", "position"]


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "color"]
    list_filter = ["project"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "role", "joined_at"]
    list_filter = ["role"]
    raw_id_fields = ["user", "project"]
