"""Admin configuration for accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Workspace, WorkspaceMember


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "first_name", "last_name", "is_staff", "date_joined"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("avatar", "job_title", "bio", "timezone")}),
    )


class WorkspaceMemberInline(admin.TabularInline):
    model = WorkspaceMember
    extra = 0
    raw_id_fields = ["user"]


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ["owner"]
    inlines = [WorkspaceMemberInline]


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "workspace", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    raw_id_fields = ["user", "workspace"]
