"""
Document models: Document, DocumentVersion, DocumentFolder.
Provides document management with versioning and folder structure.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class DocumentFolder(models.Model):
    """Folders for organizing documents within a project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="folders"
    )
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
    )
    color = models.CharField(max_length=7, default="#6B7280")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_folders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document_folders"
        ordering = ["name"]
        unique_together = ("project", "name", "parent")

    def __str__(self):
        return self.name

    @property
    def document_count(self):
        return self.documents.count()

    @property
    def full_path(self):
        """Get the full folder path including parents."""
        parts = [self.name]
        current = self.parent
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return "/".join(parts)


class Document(models.Model):
    """A document within a project, supports rich text and file attachments."""

    class DocType(models.TextChoices):
        PAGE = "page", "Page"
        WIKI = "wiki", "Wiki"
        SPEC = "spec", "Specification"
        MEETING = "meeting", "Meeting Notes"
        TEMPLATE = "template", "Template"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="documents"
    )
    folder = models.ForeignKey(
        DocumentFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    title = models.CharField(max_length=300)
    content = models.TextField(
        blank=True,
        help_text="Document content in Markdown or HTML format",
    )
    doc_type = models.CharField(
        max_length=10, choices=DocType.choices, default=DocType.PAGE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="authored_documents",
    )
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="last_edited_documents",
    )
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    word_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        ordering = ["-is_pinned", "-updated_at"]

    def __str__(self):
        return f"{self.project.key} - {self.title}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)


class DocumentVersion(models.Model):
    """Version history for a document, stores snapshots of content."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=300)
    content = models.TextField()
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="document_edits",
    )
    change_summary = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_versions"
        ordering = ["-version_number"]
        unique_together = ("document", "version_number")

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
