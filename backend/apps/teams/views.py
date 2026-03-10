"""
Team views: CRUD, member management, project assignment.
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import WorkspaceMember
from apps.projects.models import Project

from .models import Team, TeamMember, TeamProject
from .serializers import (
    AddTeamMemberSerializer,
    AssignProjectSerializer,
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamListSerializer,
    TeamMemberSerializer,
    TeamProjectSerializer,
)

User = get_user_model()


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for team CRUD and management operations."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Team.objects.filter(
            workspace__workspace_members__user=self.request.user
        ).select_related("workspace", "lead").distinct()

        workspace_id = self.request.query_params.get("workspace")
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        active_only = self.request.query_params.get("active")
        if active_only and active_only.lower() == "true":
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamListSerializer

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        """List all team members."""
        team = self.get_object()
        memberships = team.team_members.select_related("user").all()
        serializer = TeamMemberSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the team."""
        team = self.get_object()
        serializer = AddTeamMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        role = serializer.validated_data["role"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify user is a workspace member
        if not WorkspaceMember.objects.filter(
            workspace=team.workspace, user=user
        ).exists():
            return Response(
                {"detail": "User must be a workspace member first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership, created = TeamMember.objects.get_or_create(
            team=team,
            user=user,
            defaults={"role": role},
        )

        if not created:
            return Response(
                {"detail": "User is already a team member."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            TeamMemberSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path="members/(?P<member_id>[^/.]+)",
    )
    def remove_member(self, request, pk=None, member_id=None):
        """Remove a member from the team."""
        team = self.get_object()
        try:
            membership = TeamMember.objects.get(team=team, id=member_id)
        except TeamMember.DoesNotExist:
            return Response(
                {"detail": "Member not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def assign_project(self, request, pk=None):
        """Assign a project to this team."""
        team = self.get_object()
        serializer = AssignProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data["project_id"]
        try:
            project = Project.objects.get(
                id=project_id, workspace=team.workspace
            )
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found in this workspace."},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment, created = TeamProject.objects.get_or_create(
            team=team, project=project
        )

        if not created:
            return Response(
                {"detail": "Project is already assigned to this team."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            TeamProjectSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path="projects/(?P<project_id>[^/.]+)")
    def unassign_project(self, request, pk=None, project_id=None):
        """Unassign a project from this team."""
        team = self.get_object()
        try:
            assignment = TeamProject.objects.get(
                team=team, project_id=project_id
            )
        except TeamProject.DoesNotExist:
            return Response(
                {"detail": "Project assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def workload(self, request, pk=None):
        """Get workload distribution across team members."""
        team = self.get_object()
        members = team.team_members.select_related("user").all()

        from apps.tasks.models import Task

        workload_data = []
        for membership in members:
            active_tasks = Task.objects.filter(
                assignee=membership.user,
                is_archived=False,
                completed_at__isnull=True,
                project__workspace=team.workspace,
            )
            total_points = sum(
                t.story_points or 0 for t in active_tasks
            )
            workload_data.append({
                "user": {
                    "id": str(membership.user.id),
                    "email": membership.user.email,
                    "full_name": membership.user.full_name,
                },
                "role": membership.role,
                "active_tasks": active_tasks.count(),
                "total_story_points": total_points,
                "tasks_by_priority": {
                    "highest": active_tasks.filter(priority="highest").count(),
                    "high": active_tasks.filter(priority="high").count(),
                    "medium": active_tasks.filter(priority="medium").count(),
                    "low": active_tasks.filter(priority="low").count(),
                    "lowest": active_tasks.filter(priority="lowest").count(),
                },
            })

        return Response(workload_data)
