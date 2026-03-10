"""
Time tracking models: TimeEntry, Timer.
Provides time logging and active timer support for tasks.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.tasks.models import Task


class TimeEntry(models.Model):
    """A manually logged or timer-created time entry against a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="time_entries"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    description = models.TextField(blank=True)
    hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Duration in hours",
    )
    date = models.DateField(
        default=timezone.now,
        help_text="The date this work was performed",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_billable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "time_entries"
        ordering = ["-date", "-created_at"]
        verbose_name_plural = "Time entries"

    def __str__(self):
        return f"{self.user.email} - {self.task.task_key} ({self.hours}h)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the task's total time spent
        total = TimeEntry.objects.filter(task=self.task).aggregate(
            total=models.Sum("hours")
        )["total"] or Decimal("0")
        Task.objects.filter(id=self.task_id).update(time_spent_hours=total)


class Timer(models.Model):
    """An active running timer for a user on a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="timers"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="active_timers",
    )
    started_at = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    is_billable = models.BooleanField(default=True)

    class Meta:
        db_table = "timers"
        ordering = ["-started_at"]
        # Only one active timer per user
        unique_together = ("user", "task")

    def __str__(self):
        return f"Timer: {self.user.email} on {self.task.task_key}"

    @property
    def elapsed_seconds(self):
        """Seconds elapsed since the timer started."""
        return (timezone.now() - self.started_at).total_seconds()

    @property
    def elapsed_hours(self):
        """Hours elapsed since the timer started, rounded to 2 decimal places."""
        return round(Decimal(self.elapsed_seconds) / Decimal(3600), 2)

    def stop_and_create_entry(self):
        """Stop the timer and create a time entry from the elapsed time."""
        hours = self.elapsed_hours
        if hours < Decimal("0.01"):
            hours = Decimal("0.01")

        entry = TimeEntry.objects.create(
            task=self.task,
            user=self.user,
            description=self.description,
            hours=hours,
            date=self.started_at.date(),
            started_at=self.started_at,
            ended_at=timezone.now(),
            is_billable=self.is_billable,
        )
        self.delete()
        return entry
