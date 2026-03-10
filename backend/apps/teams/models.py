"""
Team models: Team, TeamMember, TeamProject.
Teams group workspace members for assignment and reporting purposes.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.accounts.models import Workspace


class Team(models.Model):
    """A team is a group of workspace members that can be assigned to projects."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="teams"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_teams",
    )
    avatar = models.ImageField(upload_to="team_avatars/", null=True, blank=True)
    color = models.CharField(max_length=7, default="#8B5CF6")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teams"
        ordering = ["name"]
        unique_together = ("workspace", "name")

    def __str__(self):
        return f"{self.workspace.name} - {self.name}"

    @property
    def member_count(self):
        return self.team_members.count()

    @property
    def active_tasks_count(self):
        """Count of active tasks assigned to team members."""
        member_ids = self.team_members.values_list("user_id", flat=True)
        from apps.tasks.models import Task
        return Task.objects.filter(
            assignee_id__in=member_ids,
            is_archived=False,
            completed_at__isnull=True,
        ).count()


class TeamMember(models.Model):
    """Membership linking a user to a team with a role."""

    class Role(models.TextChoices):
        LEAD = "lead", "Lead"
        SENIOR = "senior", "Senior Member"
        MEMBER = "member", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="team_members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_members"
        unique_together = ("team", "user")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.team.name} ({self.role})"


class TeamProject(models.Model):
    """Associates a team with projects they are responsible for."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="team_projects"
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="team_assignments"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_projects"
        unique_together = ("team", "project")
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.team.name} -> {self.project.name}"
