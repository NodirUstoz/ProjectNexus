"""
Milestone models: Milestone, MilestoneTask linking.
Milestones mark key checkpoints and deliverables within a project timeline.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class Milestone(models.Model):
    """A milestone represents a key deliverable or checkpoint in a project."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.NOT_STARTED
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_milestones",
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)
    color = models.CharField(max_length=7, default="#6366F1")
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "milestones"
        ordering = ["due_date", "position"]

    def __str__(self):
        return f"{self.project.key} - {self.title}"

    @property
    def progress_percentage(self):
        """Calculate completion percentage based on linked tasks."""
        total = self.milestone_tasks.count()
        if total == 0:
            return 0
        completed = self.milestone_tasks.filter(
            task__column__is_done_column=True
        ).count()
        return round((completed / total) * 100, 1)

    @property
    def total_tasks(self):
        return self.milestone_tasks.count()

    @property
    def completed_tasks(self):
        return self.milestone_tasks.filter(
            task__column__is_done_column=True
        ).count()

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status == self.Status.COMPLETED:
            return False
        return self.due_date < timezone.now().date()


class MilestoneTask(models.Model):
    """Link between a milestone and a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    milestone = models.ForeignKey(
        Milestone, on_delete=models.CASCADE, related_name="milestone_tasks"
    )
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="milestone_links"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="milestone_task_additions",
    )

    class Meta:
        db_table = "milestone_tasks"
        unique_together = ("milestone", "task")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.milestone.title} -> {self.task.task_key}"
