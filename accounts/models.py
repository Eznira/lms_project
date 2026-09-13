from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("role", self.model.Role.ADMIN)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")

        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    biography = models.TextField(
        blank=True,
    )

    profile_photo = models.ImageField(
        upload_to="students/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class InstructorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )

    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    biography = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    profile_photo = models.ImageField(
        upload_to="instructors/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"
