from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .models import (
    EmailVerificationToken,
    InstructorProfile,
    StudentProfile,
)

User = get_user_model()

class StrictFieldsMixin:
    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())
        provided_fields = set(data.keys())

        unknown_fields = provided_fields - allowed_fields

        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )

        return super().to_internal_value(data)

class StudentProfileSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [  # noqa: RUF012
            "phone",
            "biography",
            "profile_photo",
        ]

class InstructorProfileSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = [  # noqa: RUF012
            "qualification",
            "specialization",
            "biography",
            "phone",
            "profile_photo",
        ]

class ProfileSerializer(serializers.ModelSerializer):
    profile = serializers.DictField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.role == User.Role.STUDENT:
            data["profile"] = StudentProfileSerializer(instance.student_profile).data

        elif instance.role == User.Role.INSTRUCTOR:
            data["profile"] = InstructorProfileSerializer(
                instance.instructor_profile
            ).data

        else:
            data["profile"] = {}

        return data

    def validate_profile(self, value):
        if self.instance.role == User.Role.STUDENT:
            serializer = StudentProfileSerializer(
                data=value,
                partial=True,
            )

        elif self.instance.role == User.Role.INSTRUCTOR:
            serializer = InstructorProfileSerializer(
                data=value,
                partial=True,
            )

        else:
            raise serializers.ValidationError(
                "Admin profile updates are not supported."
            )

        serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})

        instance.first_name = validated_data.get(
            "first_name",
            instance.first_name,
        )

        instance.last_name = validated_data.get(
            "last_name",
            instance.last_name,
        )

        instance.save()

        if instance.role == User.Role.STUDENT:
            profile = instance.student_profile

        elif instance.role == User.Role.INSTRUCTOR:
            profile = instance.instructor_profile

        else:
            return instance

        for field, value in profile_data.items():
            setattr(profile, field, value)

        profile.save()

        return instance

class RegisterSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User

        fields = [
            "email",
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

        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            # IMPORTANT
            role=User.Role.STUDENT,
            is_active=False,
            email_verified=False,
        )  # type: ignore

        StudentProfile.objects.create(
            user=user,
        )

        EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        return user

class VerifyEmailSerializer(StrictFieldsMixin, serializers.Serializer):
    token = serializers.UUIDField()

class PasswordResetRequestSerializer(StrictFieldsMixin, serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(StrictFieldsMixin, serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )

        return attrs

class InstructorCreateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    qualification = serializers.CharField()
    specialization = serializers.CharField()
    biography = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    profile_photo = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User

        fields = [
            "email",
            "first_name",
            "last_name",
            "qualification",
            "specialization",
            "biography",
            "phone",
            "profile_photo",
        ]

    def create(self, validated_data):
        qualification = validated_data.pop("qualification")

        specialization = validated_data.pop("specialization")

        biography = validated_data.pop(
            "biography",
            "",
        )

        phone = validated_data.pop(
            "phone",
            "",
        )

        profile_photo = validated_data.pop(
            "profile_photo",
            None,
        )

        # Generate a temporary unusable password.
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=User.Role.INSTRUCTOR,
            is_active=False,
            email_verified=False,
        )  # type: ignore

        InstructorProfile.objects.create(
            user=user,
            qualification=qualification,
            specialization=specialization,
            biography=biography,
            phone=phone,
            profile_photo=profile_photo,
        )

        EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        return user

class InstructorSetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        return attrs
