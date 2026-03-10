"""
Account views: registration, profile, workspace management.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Workspace, WorkspaceMember
from .permissions import IsWorkspaceAdmin, IsWorkspaceMember
from .serializers import (
    CustomTokenObtainPairSerializer,
    InviteMemberSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    WorkspaceDetailSerializer,
    WorkspaceMemberSerializer,
    WorkspaceSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response(
            {
                "message": "Account created successfully.",
                "user": user_data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login endpoint that returns user data with tokens."""

    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update current user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class WorkspaceViewSet(viewsets.ModelViewSet):
    """CRUD operations for workspaces."""

    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(
            workspace_members__user=self.request.user
        ).distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WorkspaceDetailSerializer
        return WorkspaceSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsWorkspaceAdmin],
    )
    def invite(self, request, pk=None):
        """Invite a user to the workspace."""
        workspace = self.get_object()
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]
        user = User.objects.get(email=email)

        if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            return Response(
                {"detail": "User is already a member of this workspace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = WorkspaceMember.objects.create(
            workspace=workspace, user=user, role=role
        )
        return Response(
            WorkspaceMemberSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path="members/(?P<member_id>[^/.]+)",
        permission_classes=[permissions.IsAuthenticated, IsWorkspaceAdmin],
    )
    def remove_member(self, request, pk=None, member_id=None):
        """Remove a member from the workspace."""
        workspace = self.get_object()
        try:
            membership = WorkspaceMember.objects.get(
                workspace=workspace, id=member_id
            )
        except WorkspaceMember.DoesNotExist:
            return Response(
                {"detail": "Member not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if membership.role == WorkspaceMember.Role.OWNER:
            return Response(
                {"detail": "Cannot remove the workspace owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsWorkspaceMember],
    )
    def members(self, request, pk=None):
        """List all members of the workspace."""
        workspace = self.get_object()
        memberships = workspace.workspace_members.select_related("user").all()
        serializer = WorkspaceMemberSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        """Leave a workspace."""
        workspace = self.get_object()
        membership = WorkspaceMember.objects.filter(
            workspace=workspace, user=request.user
        ).first()

        if not membership:
            return Response(
                {"detail": "You are not a member of this workspace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if membership.role == WorkspaceMember.Role.OWNER:
            return Response(
                {"detail": "Owner cannot leave the workspace. Transfer ownership first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response(
            {"detail": "You have left the workspace."},
            status=status.HTTP_200_OK,
        )
