"""
Account models: User, Workspace, WorkspaceMember.
"""

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional profile fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class Workspace(models.Model):
    """
    A workspace is the top-level organizational unit.
    Each workspace can contain multiple projects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="workspace_logos/", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="WorkspaceMember",
        related_name="workspaces",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workspaces"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    """Membership relationship between User and Workspace with role."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="workspace_members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workspace_members"
        unique_together = ("workspace", "user")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.role})"
