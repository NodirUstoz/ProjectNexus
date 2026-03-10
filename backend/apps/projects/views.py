"""
Project views: CRUD, board management, member management.
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import WorkspaceMember

from .models import Board, BoardColumn, Label, Project, ProjectMember
from .serializers import (
    BoardColumnReorderSerializer,
    BoardColumnSerializer,
    BoardSerializer,
    LabelSerializer,
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for project CRUD operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.filter(
            workspace__workspace_members__user=self.request.user,
            is_archived=False,
        ).select_related("lead", "workspace").distinct()

        workspace_id = self.request.query_params.get("workspace")
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ProjectCreateSerializer
        if self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["workspace_id"] = self.request.query_params.get("workspace")
        return context

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Archive a project."""
        project = self.get_object()
        project.is_archived = True
        project.save(update_fields=["is_archived"])
        return Response({"detail": "Project archived."})

    @action(detail=True, methods=["post"])
    def unarchive(self, request, pk=None):
        """Unarchive a project."""
        project = self.get_object()
        project.is_archived = False
        project.save(update_fields=["is_archived"])
        return Response({"detail": "Project unarchived."})

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the project."""
        project = self.get_object()
        user_id = request.data.get("user_id")
        role = request.data.get("role", ProjectMember.Role.MEMBER)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify user is a workspace member
        if not WorkspaceMember.objects.filter(
            workspace=project.workspace, user=user
        ).exists():
            return Response(
                {"detail": "User must be a workspace member first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership, created = ProjectMember.objects.get_or_create(
            project=project,
            user=user,
            defaults={"role": role},
        )

        if not created:
            return Response(
                {"detail": "User is already a project member."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ProjectMemberSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def board(self, request, pk=None):
        """Get the default board for a project with columns and tasks."""
        project = self.get_object()
        board = project.boards.filter(is_default=True).first()
        if not board:
            board = project.boards.first()

        if not board:
            return Response(
                {"detail": "No board found for this project."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BoardSerializer(board)
        return Response(serializer.data)


class BoardViewSet(viewsets.ModelViewSet):
    """ViewSet for board CRUD operations."""

    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(
            project__workspace__workspace_members__user=self.request.user
        ).select_related("project").distinct()

    @action(detail=True, methods=["post"])
    def reorder_columns(self, request, pk=None):
        """Reorder columns within a board."""
        board = self.get_object()
        serializer = BoardColumnReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        column_ids = serializer.validated_data["column_ids"]
        for position, column_id in enumerate(column_ids):
            BoardColumn.objects.filter(
                id=column_id, board=board
            ).update(position=position)

        return Response({"detail": "Columns reordered."})


class BoardColumnViewSet(viewsets.ModelViewSet):
    """ViewSet for board column operations."""

    serializer_class = BoardColumnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BoardColumn.objects.filter(
            board__project__workspace__workspace_members__user=self.request.user
        ).select_related("board").distinct()

    def perform_create(self, serializer):
        board_id = self.request.data.get("board_id")
        board = Board.objects.get(id=board_id)
        max_position = board.columns.count()
        serializer.save(board=board, position=max_position)


class LabelViewSet(viewsets.ModelViewSet):
    """ViewSet for project label operations."""

    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get("project")
        queryset = Label.objects.filter(
            project__workspace__workspace_members__user=self.request.user
        ).distinct()
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        project_id = self.request.data.get("project_id")
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)
