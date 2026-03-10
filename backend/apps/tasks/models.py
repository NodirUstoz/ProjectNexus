"""
Task models: Task, Subtask, TaskComment, TaskAttachment, TaskHistory.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import BoardColumn, Label, Project


class Task(models.Model):
    """Core task model representing a work item."""

    class Priority(models.TextChoices):
        LOWEST = "lowest", "Lowest"
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        HIGHEST = "highest", "Highest"

    class TaskType(models.TextChoices):
        STORY = "story", "Story"
        TASK = "task", "Task"
        BUG = "bug", "Bug"
        EPIC = "epic", "Epic"
        SUBTASK = "subtask", "Subtask"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    column = models.ForeignKey(
        BoardColumn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    sprint = models.ForeignKey(
        "sprints.Sprint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks",
    )

    # Identifiers
    task_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    # Classification
    task_type = models.CharField(
        max_length=10, choices=TaskType.choices, default=TaskType.TASK
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    labels = models.ManyToManyField(Label, blank=True, related_name="tasks")

    # Assignment
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_tasks",
    )

    # Estimation
    story_points = models.PositiveIntegerField(null=True, blank=True)
    original_estimate_hours = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    time_spent_hours = models.DecimalField(
        max_digits=7, decimal_places=2, default=0
    )

    # Dates
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Position for ordering within a column
    position = models.PositiveIntegerField(default=0)

    # Metadata
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["position", "-created_at"]
        unique_together = ("project", "task_number")

    def __str__(self):
        return f"{self.project.key}-{self.task_number}: {self.title}"

    @property
    def task_key(self):
        return f"{self.project.key}-{self.task_number}"

    def save(self, *args, **kwargs):
        if not self.task_number:
            self.task_number = self.project.get_next_task_number()
        super().save(*args, **kwargs)


class Subtask(models.Model):
    """Lightweight checklist-style subtask within a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="checklist_items"
    )
    title = models.CharField(max_length=300)
    is_completed = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subtasks"
        ordering = ["position"]

    def __str__(self):
        return self.title


class TaskComment(models.Model):
    """Comments on a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "task_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.email} on {self.task.task_key}"


class TaskAttachment(models.Model):
    """File attachments on a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="attachments"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
    )
    file = models.FileField(upload_to="task_attachments/%Y/%m/")
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    content_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_attachments"
        ordering = ["-created_at"]

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = self.file.name
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class TaskHistory(models.Model):
    """Audit log for task changes."""

    class ChangeType(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        MOVED = "moved", "Moved"
        ASSIGNED = "assigned", "Assigned"
        COMMENTED = "commented", "Commented"
        ATTACHMENT = "attachment", "Attachment Added"
        STATUS_CHANGE = "status_change", "Status Changed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="history"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="task_history_entries",
    )
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    field_name = models.CharField(max_length=50, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_history"
        ordering = ["-created_at"]
        verbose_name_plural = "Task histories"

    def __str__(self):
        return f"{self.task.task_key} - {self.change_type} by {self.user}"
