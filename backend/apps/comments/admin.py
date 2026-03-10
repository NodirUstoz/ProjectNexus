"""Admin configuration for comments."""

from django.contrib import admin

from .models import Comment, CommentReaction


class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 0
    raw_id_fields = ["user"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "content_type",
        "body_preview",
        "parent",
        "is_resolved",
        "reply_count",
        "created_at",
    ]
    list_filter = ["content_type", "is_resolved", "is_edited", "created_at"]
    search_fields = ["body"]
    raw_id_fields = ["author", "parent"]
    inlines = [CommentReactionInline]

    def body_preview(self, obj):
        return obj.body[:80] + "..." if len(obj.body) > 80 else obj.body
    body_preview.short_description = "Body"


@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ["comment", "user", "emoji", "created_at"]
    list_filter = ["emoji"]
    raw_id_fields = ["comment", "user"]
