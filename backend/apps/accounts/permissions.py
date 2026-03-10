"""
Custom permissions for workspace and project access control.
"""

from rest_framework import permissions

from .models import WorkspaceMember


class IsWorkspaceMember(permissions.BasePermission):
    """Allow access only to members of the workspace."""

    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, "workspace", obj)
        return WorkspaceMember.objects.filter(
            workspace=workspace, user=request.user
        ).exists()


class IsWorkspaceAdmin(permissions.BasePermission):
    """Allow access only to workspace owners and admins."""

    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, "workspace", obj)
        return WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN],
        ).exists()


class IsWorkspaceOwner(permissions.BasePermission):
    """Allow access only to the workspace owner."""

    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, "workspace", obj)
        return workspace.owner == request.user


class IsWorkspaceMemberReadOnly(permissions.BasePermission):
    """
    Allow read access to all workspace members.
    Write access only for admins and owners.
    """

    def has_object_permission(self, request, view, obj):
        workspace = getattr(obj, "workspace", obj)
        membership = WorkspaceMember.objects.filter(
            workspace=workspace, user=request.user
        ).first()

        if not membership:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return membership.role in [
            WorkspaceMember.Role.OWNER,
            WorkspaceMember.Role.ADMIN,
        ]


class IsProjectMemberOrWorkspaceAdmin(permissions.BasePermission):
    """
    Allow access if the user is a project member or workspace admin.
    """

    def has_object_permission(self, request, view, obj):
        from apps.projects.models import ProjectMember

        project = getattr(obj, "project", obj)
        workspace = project.workspace

        # Check workspace admin
        is_workspace_admin = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN],
        ).exists()

        if is_workspace_admin:
            return True

        # Check project member
        return ProjectMember.objects.filter(
            project=project, user=request.user
        ).exists()
