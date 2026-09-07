from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import (
    InstructorProfile,
    StudentProfile,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = (
        ("Account Information", {
            "fields": (
                "username",
                "password",
            )
        }),
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
            )
        }),
        ("LMS Information", {
            "fields": (
                "role",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
    )

    add_fieldsets = (
        ("Account Information", {
            "fields": (
                "username",
                "password1",
                "password2",
            )
        }),
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
            )
        }),
        ("LMS Information", {
            "fields": (
                "role",
            )
        }),
        ("Instructor Information", {
            "fields": (
                "qualification",
                "specialization",
                "biography",
                "phone",
                "profile_photo",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.role == User.Role.INSTRUCTOR:
            profile, _ = InstructorProfile.objects.get_or_create(
                user=obj
            )

            profile.qualification = form.cleaned_data.get(
                "qualification", ""
            )
            profile.specialization = form.cleaned_data.get(
                "specialization", ""
            )
            profile.biography = form.cleaned_data.get(
                "biography", ""
            )
            profile.phone = form.cleaned_data.get(
                "phone", ""
            )

            if form.cleaned_data.get("profile_photo"):
                profile.profile_photo = form.cleaned_data[
                    "profile_photo"
                ]

            profile.save()

            # An instructor should not have a student profile.
            StudentProfile.objects.filter(user=obj).delete()

        elif obj.role == User.Role.STUDENT:
            StudentProfile.objects.get_or_create(user=obj)

            # A student should not have an instructor profile.
            InstructorProfile.objects.filter(user=obj).delete()

        else:
            # ADMIN users don't need either profile.
            StudentProfile.objects.filter(user=obj).delete()
            InstructorProfile.objects.filter(user=obj).delete()