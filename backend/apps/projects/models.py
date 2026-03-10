"""
Project models: Project, Board, BoardColumn, Label, ProjectMember.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.accounts.models import Workspace


class Project(models.Model):
    """A project belongs to a workspace and contains boards and tasks."""

    class ProjectType(models.TextChoices):
        KANBAN = "kanban", "Kanban"
        SCRUM = "scrum", "Scrum"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=200)
    key = models.CharField(
        max_length=10,
        help_text="Short project key for task identifiers (e.g., PRJ)",
    )
    description = models.TextField(blank=True)
    project_type = models.CharField(
        max_length=10,
        choices=ProjectType.choices,
        default=ProjectType.KANBAN,
    )
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_projects",
    )
    icon = models.CharField(max_length=10, default="📋")
    color = models.CharField(max_length=7, default="#4A90D9")
    is_archived = models.BooleanField(default=False)
    task_counter = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        unique_together = ("workspace", "key")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.key} - {self.name}"

    def get_next_task_number(self):
        """Generate the next sequential task number for this project."""
        self.task_counter += 1
        self.save(update_fields=["task_counter"])
        return self.task_counter


class ProjectMember(models.Model):
    """Membership relationship between User and Project with role."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_members"
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.role})"


class Board(models.Model):
    """A board represents a view of tasks within a project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="boards"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "boards"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.project.key} - {self.name}"


class BoardColumn(models.Model):
    """A column within a board (e.g., To Do, In Progress, Done)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="columns"
    )
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#E2E8F0")
    wip_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Work-in-progress limit for this column",
    )
    is_done_column = models.BooleanField(
        default=False,
        help_text="Tasks in this column are considered completed",
    )

    class Meta:
        db_table = "board_columns"
        ordering = ["position"]

    def __str__(self):
        return f"{self.board.name} - {self.name}"


class Label(models.Model):
    """Labels for categorizing tasks within a project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="labels"
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#3B82F6")

    class Meta:
        db_table = "labels"
        unique_together = ("project", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name
