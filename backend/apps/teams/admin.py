"""Admin configuration for teams."""

from django.contrib import admin

from .models import Team, TeamMember, TeamProject


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    raw_id_fields = ["user"]


class TeamProjectInline(admin.TabularInline):
    model = TeamProject
    extra = 0
    raw_id_fields = ["project"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "workspace", "lead", "member_count", "is_active", "created_at"]
    list_filter = ["is_active", "workspace", "created_at"]
    search_fields = ["name", "description"]
    raw_id_fields = ["workspace", "lead"]
    inlines = [TeamMemberInline, TeamProjectInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "team", "role", "joined_at"]
    list_filter = ["role"]
    raw_id_fields = ["user", "team"]
