from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    qualification = forms.CharField(
        max_length=255,
        required=False,
    )
    specialization = forms.CharField(
        max_length=255,
        required=False,
    )
    biography = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
    )
    profile_photo = forms.ImageField(
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
        )


class CustomUserChangeForm(UserChangeForm):
    qualification = forms.CharField(
        max_length=255,
        required=False,
    )
    specialization = forms.CharField(
        max_length=255,
        required=False,
    )
    biography = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
    )
    profile_photo = forms.ImageField(
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
        )
