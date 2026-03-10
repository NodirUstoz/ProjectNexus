"""
Sprint models: Sprint, SprintGoal.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class Sprint(models.Model):
    """Sprint for Scrum-based project management."""

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sprints"
    )
    name = models.CharField(max_length=200)
    goal = models.TextField(blank=True, help_text="Sprint goal description")
    sprint_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PLANNING
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_sprints",
    )
    velocity = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual story points completed in this sprint",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sprints"
        ordering = ["-sprint_number"]
        unique_together = ("project", "sprint_number")

    def __str__(self):
        return f"{self.project.key} Sprint {self.sprint_number}: {self.name}"

    @property
    def total_story_points(self):
        """Sum of story points for all tasks in this sprint."""
        return self.tasks.aggregate(
            total=models.Sum("story_points")
        )["total"] or 0

    @property
    def completed_story_points(self):
        """Sum of story points for completed tasks."""
        return self.tasks.filter(
            column__is_done_column=True
        ).aggregate(
            total=models.Sum("story_points")
        )["total"] or 0

    @property
    def task_count(self):
        return self.tasks.count()

    @property
    def completed_task_count(self):
        return self.tasks.filter(column__is_done_column=True).count()

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0


class SprintGoal(models.Model):
    """Individual goals within a sprint for tracking purposes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sprint = models.ForeignKey(
        Sprint, on_delete=models.CASCADE, related_name="goals"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sprint_goals"
        ordering = ["created_at"]

    def __str__(self):
        status = "Done" if self.is_achieved else "Pending"
        return f"[{status}] {self.title}"
