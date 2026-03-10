"""
Document views: CRUD, version management, folder operations.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document, DocumentFolder, DocumentVersion
from .serializers import (
    DocumentCreateSerializer,
    DocumentDetailSerializer,
    DocumentFolderSerializer,
    DocumentListSerializer,
    DocumentUpdateSerializer,
    DocumentVersionSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for document CRUD and version management."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Document.objects.filter(
            project__workspace__workspace_members__user=self.request.user,
            is_archived=False,
        ).select_related("project", "author", "last_edited_by", "folder").distinct()

        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        folder_id = self.request.query_params.get("folder")
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        elif self.request.query_params.get("root") == "true":
            queryset = queryset.filter(folder__isnull=True)

        doc_type = self.request.query_params.get("type")
        if doc_type:
            queryset = queryset.filter(doc_type=doc_type)

        pinned = self.request.query_params.get("pinned")
        if pinned and pinned.lower() == "true":
            queryset = queryset.filter(is_pinned=True)

        templates = self.request.query_params.get("templates")
        if templates and templates.lower() == "true":
            queryset = queryset.filter(is_template=True)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer
        if self.action in ["update", "partial_update"]:
            return DocumentUpdateSerializer
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentListSerializer

    @action(detail=True, methods=["post"])
    def pin(self, request, pk=None):
        """Toggle pin status of a document."""
        document = self.get_object()
        document.is_pinned = not document.is_pinned
        document.save(update_fields=["is_pinned", "updated_at"])
        return Response(DocumentListSerializer(document).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Archive a document."""
        document = self.get_object()
        document.is_archived = True
        document.save(update_fields=["is_archived", "updated_at"])
        return Response({"detail": "Document archived."})

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        """List all versions of a document."""
        document = self.get_object()
        versions = document.versions.select_related("edited_by").all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="versions/(?P<version_number>[0-9]+)/restore")
    def restore_version(self, request, pk=None, version_number=None):
        """Restore a document to a specific version."""
        document = self.get_object()
        try:
            target_version = document.versions.get(
                version_number=version_number
            )
        except DocumentVersion.DoesNotExist:
            return Response(
                {"detail": "Version not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        document.title = target_version.title
        document.content = target_version.content
        document.version += 1
        document.last_edited_by = request.user
        document.save()

        DocumentVersion.objects.create(
            document=document,
            version_number=document.version,
            title=document.title,
            content=document.content,
            edited_by=request.user,
            change_summary=f"Restored from version {version_number}",
        )

        return Response(DocumentDetailSerializer(document).data)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Create a copy of a document."""
        original = self.get_object()
        copy = Document.objects.create(
            project=original.project,
            folder=original.folder,
            title=f"{original.title} (Copy)",
            content=original.content,
            doc_type=original.doc_type,
            author=request.user,
            last_edited_by=request.user,
        )

        DocumentVersion.objects.create(
            document=copy,
            version_number=1,
            title=copy.title,
            content=copy.content,
            edited_by=request.user,
            change_summary=f"Duplicated from {original.title}",
        )

        return Response(
            DocumentDetailSerializer(copy).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentFolderViewSet(viewsets.ModelViewSet):
    """ViewSet for document folder CRUD operations."""

    serializer_class = DocumentFolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = DocumentFolder.objects.filter(
            project__workspace__workspace_members__user=self.request.user
        ).select_related("project", "created_by", "parent").distinct()

        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        root = self.request.query_params.get("root")
        if root and root.lower() == "true":
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def perform_create(self, serializer):
        project_id = self.request.data.get("project_id")
        from apps.projects.models import Project
        project = Project.objects.get(id=project_id)
        serializer.save(project=project, created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def tree(self, request, pk=None):
        """Get folder tree structure starting from this folder."""
        folder = self.get_object()

        def build_tree(parent_folder):
            result = DocumentFolderSerializer(parent_folder).data
            children = parent_folder.subfolders.all()
            result["children"] = [build_tree(child) for child in children]
            return result

        return Response(build_tree(folder))
