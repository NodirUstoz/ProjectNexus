"""
Account serializers for user registration, authentication, and workspace management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Workspace, WorkspaceMember

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "job_title",
            "bio",
            "timezone",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "date_joined"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user data in response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Serializer for workspace membership."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for workspace data."""

    owner = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "owner",
            "member_count",
            "current_user_role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.workspace_members.count()

    def get_current_user_role(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            membership = obj.workspace_members.filter(user=request.user).first()
            return membership.role if membership else None
        return None

    def create(self, validated_data):
        user = self.context["request"].user
        slug = slugify(validated_data["name"])
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data["slug"] = slug
        validated_data["owner"] = user

        workspace = Workspace.objects.create(**validated_data)
        WorkspaceMember.objects.create(
            workspace=workspace, user=user, role=WorkspaceMember.Role.OWNER
        )
        return workspace


class WorkspaceDetailSerializer(WorkspaceSerializer):
    """Extended workspace serializer with member list."""

    members = serializers.SerializerMethodField()

    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + ["members"]

    def get_members(self, obj):
        memberships = obj.workspace_members.select_related("user").all()
        return WorkspaceMemberSerializer(memberships, many=True).data


class InviteMemberSerializer(serializers.Serializer):
    """Serializer for inviting a member to a workspace."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=WorkspaceMember.Role.choices,
        default=WorkspaceMember.Role.MEMBER,
    )

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email address."
            )
        return value
