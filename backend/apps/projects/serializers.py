"""
Project serializers for CRUD and nested representations.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Board, BoardColumn, Label, Project, ProjectMember


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color"]
        read_only_fields = ["id"]


class BoardColumnSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = BoardColumn
        fields = ["id", "name", "position", "color", "wip_limit", "is_done_column", "task_count"]
        read_only_fields = ["id"]

    def get_task_count(self, obj):
        return obj.tasks.count()


class BoardSerializer(serializers.ModelSerializer):
    columns = BoardColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "name", "description", "is_default", "columns", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Compact serializer for project listings."""

    lead = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "key",
            "description",
            "project_type",
            "lead",
            "icon",
            "color",
            "is_archived",
            "member_count",
            "task_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.project_members.count()

    def get_task_count(self, obj):
        return obj.tasks.count()


class ProjectDetailSerializer(ProjectListSerializer):
    """Full serializer for project detail view."""

    boards = BoardSerializer(many=True, read_only=True)
    members = ProjectMemberSerializer(source="project_members", many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)

    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields + ["boards", "members", "labels"]


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new project with default board and columns."""

    class Meta:
        model = Project
        fields = ["name", "key", "description", "project_type", "lead", "icon", "color"]

    def validate_key(self, value):
        return value.upper()

    def create(self, validated_data):
        workspace_id = self.context["view"].kwargs.get("workspace_id")
        if not workspace_id:
            workspace_id = self.context["request"].data.get("workspace_id")

        from apps.accounts.models import Workspace

        workspace = Workspace.objects.get(id=workspace_id)
        validated_data["workspace"] = workspace

        project = Project.objects.create(**validated_data)

        # Add creator as project admin
        ProjectMember.objects.create(
            project=project,
            user=self.context["request"].user,
            role=ProjectMember.Role.ADMIN,
        )

        # Create default board with columns
        board = Board.objects.create(
            project=project, name="Main Board", is_default=True
        )

        if project.project_type == Project.ProjectType.SCRUM:
            default_columns = [
                ("To Do", "#E2E8F0", False),
                ("In Progress", "#3B82F6", False),
                ("In Review", "#F59E0B", False),
                ("Done", "#10B981", True),
            ]
        else:
            default_columns = [
                ("Backlog", "#94A3B8", False),
                ("To Do", "#E2E8F0", False),
                ("In Progress", "#3B82F6", False),
                ("In Review", "#F59E0B", False),
                ("Done", "#10B981", True),
            ]

        for idx, (name, color, is_done) in enumerate(default_columns):
            BoardColumn.objects.create(
                board=board,
                name=name,
                position=idx,
                color=color,
                is_done_column=is_done,
            )

        # Create default labels
        default_labels = [
            ("Bug", "#EF4444"),
            ("Feature", "#3B82F6"),
            ("Enhancement", "#8B5CF6"),
            ("Documentation", "#06B6D4"),
            ("Urgent", "#DC2626"),
        ]
        for name, color in default_labels:
            Label.objects.create(project=project, name=name, color=color)

        return project


class BoardColumnReorderSerializer(serializers.Serializer):
    """Serializer for reordering board columns."""

    column_ids = serializers.ListField(
        child=serializers.UUIDField(), min_length=1
    )
