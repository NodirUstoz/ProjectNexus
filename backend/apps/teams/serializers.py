"""
Team serializers for CRUD operations and member management.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.projects.serializers import ProjectListSerializer

from .models import Team, TeamMember, TeamProject


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team membership."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class TeamProjectSerializer(serializers.ModelSerializer):
    """Serializer for team-project associations."""

    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = TeamProject
        fields = ["id", "project", "assigned_at"]
        read_only_fields = ["id", "assigned_at"]


class TeamListSerializer(serializers.ModelSerializer):
    """Compact serializer for team listings."""

    lead = UserSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    active_tasks_count = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "lead",
            "avatar",
            "color",
            "is_active",
            "member_count",
            "active_tasks_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamDetailSerializer(TeamListSerializer):
    """Full serializer for team detail view."""

    members = TeamMemberSerializer(source="team_members", many=True, read_only=True)
    projects = TeamProjectSerializer(source="team_projects", many=True, read_only=True)

    class Meta(TeamListSerializer.Meta):
        fields = TeamListSerializer.Meta.fields + ["members", "projects"]


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new team."""

    class Meta:
        model = Team
        fields = ["name", "description", "lead", "color"]

    def create(self, validated_data):
        workspace_id = self.context["request"].data.get("workspace_id")
        if not workspace_id:
            workspace_id = self.context["view"].kwargs.get("workspace_id")

        from apps.accounts.models import Workspace

        workspace = Workspace.objects.get(id=workspace_id)
        validated_data["workspace"] = workspace

        team = Team.objects.create(**validated_data)

        # Add creator as team lead
        TeamMember.objects.create(
            team=team,
            user=self.context["request"].user,
            role=TeamMember.Role.LEAD,
        )

        # If a different lead was specified, add them too
        lead = validated_data.get("lead")
        if lead and lead != self.context["request"].user:
            TeamMember.objects.get_or_create(
                team=team,
                user=lead,
                defaults={"role": TeamMember.Role.LEAD},
            )

        return team


class AddTeamMemberSerializer(serializers.Serializer):
    """Serializer for adding members to a team."""

    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(
        choices=TeamMember.Role.choices,
        default=TeamMember.Role.MEMBER,
    )


class AssignProjectSerializer(serializers.Serializer):
    """Serializer for assigning a project to a team."""

    project_id = serializers.UUIDField()
