from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
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