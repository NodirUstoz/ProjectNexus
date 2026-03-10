"""Admin configuration for documents."""

from django.contrib import admin

from .models import Document, DocumentFolder, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    raw_id_fields = ["edited_by"]
    readonly_fields = ["version_number", "created_at"]


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "parent", "document_count", "created_by", "created_at"]
    list_filter = ["project", "created_at"]
    search_fields = ["name"]
    raw_id_fields = ["project", "parent", "created_by"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "project",
        "doc_type",
        "author",
        "version",
        "word_count",
        "is_pinned",
        "updated_at",
    ]
    list_filter = ["doc_type", "is_pinned", "is_archived", "is_template"]
    search_fields = ["title", "content"]
    raw_id_fields = ["project", "folder", "author", "last_edited_by"]
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ["document", "version_number", "edited_by", "change_summary", "created_at"]
    raw_id_fields = ["document", "edited_by"]
