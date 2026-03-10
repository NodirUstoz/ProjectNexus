"""
Document serializers for CRUD, versioning, and folder management.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Document, DocumentFolder, DocumentVersion


class DocumentFolderSerializer(serializers.ModelSerializer):
    """Serializer for document folders."""

    created_by = UserSerializer(read_only=True)
    document_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    subfolder_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = [
            "id",
            "name",
            "parent",
            "color",
            "created_by",
            "document_count",
            "subfolder_count",
            "full_path",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_subfolder_count(self, obj):
        return obj.subfolders.count()


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for document version history."""

    edited_by = UserSerializer(read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "version_number",
            "title",
            "content",
            "edited_by",
            "change_summary",
            "created_at",
        ]


class DocumentListSerializer(serializers.ModelSerializer):
    """Compact serializer for document listings."""

    author = UserSerializer(read_only=True)
    last_edited_by = UserSerializer(read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True, default=None)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "doc_type",
            "author",
            "last_edited_by",
            "folder",
            "folder_name",
            "is_pinned",
            "is_archived",
            "is_template",
            "version",
            "word_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "last_edited_by", "version", "word_count", "created_at", "updated_at"]


class DocumentDetailSerializer(DocumentListSerializer):
    """Full serializer for document detail view with content and versions."""

    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta(DocumentListSerializer.Meta):
        fields = DocumentListSerializer.Meta.fields + ["content", "versions"]


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new document."""

    class Meta:
        model = Document
        fields = ["title", "content", "doc_type", "folder", "is_template"]

    def create(self, validated_data):
        project_id = self.context["view"].kwargs.get("project_id")
        if not project_id:
            project_id = self.context["request"].data.get("project_id")

        from apps.projects.models import Project

        project = Project.objects.get(id=project_id)
        user = self.context["request"].user

        validated_data["project"] = project
        validated_data["author"] = user
        validated_data["last_edited_by"] = user

        document = Document.objects.create(**validated_data)

        # Create initial version
        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            title=document.title,
            content=document.content,
            edited_by=user,
            change_summary="Initial version",
        )

        return document


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a document with version tracking."""

    change_summary = serializers.CharField(required=False, default="")

    class Meta:
        model = Document
        fields = ["title", "content", "doc_type", "folder", "is_pinned", "change_summary"]

    def update(self, instance, validated_data):
        change_summary = validated_data.pop("change_summary", "")
        user = self.context["request"].user

        # Check if content has changed
        content_changed = (
            validated_data.get("content") is not None
            and validated_data.get("content") != instance.content
        )
        title_changed = (
            validated_data.get("title") is not None
            and validated_data.get("title") != instance.title
        )

        instance = super().update(instance, validated_data)

        # Create new version if content or title changed
        if content_changed or title_changed:
            instance.version += 1
            instance.last_edited_by = user
            instance.save(update_fields=["version", "last_edited_by", "updated_at"])

            DocumentVersion.objects.create(
                document=instance,
                version_number=instance.version,
                title=instance.title,
                content=instance.content,
                edited_by=user,
                change_summary=change_summary or f"Updated by {user.full_name}",
            )

        return instance
