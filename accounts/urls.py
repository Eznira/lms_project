from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    InstructorCreateView,
    InstructorSetPasswordView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RegisterView,
    VerifyEmailView,
)

urlpatterns = [
    # Registration
    path("register/", RegisterView.as_view(), name="register"),
    # Login
    path("login/", LoginView.as_view(), name="login"),
    # Refresh JWT
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Logout
    path("logout/", LogoutView.as_view(), name="logout"),
    # Email verification
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    # Instructor
    path("instructors/", InstructorCreateView.as_view(), name="instructor-create"),
    path(
        "instructors/set-password/",
        InstructorSetPasswordView.as_view(),
        name="instructor-set-password",
    ),
    # Password reset
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),

    # # Test view to get the current logged-in user's information
    # path("me/", MeView.as_view(), name="me"),
    # # Test view for instructor permission
    # path("instructor-test/", InstructorTestView.as_view(), name="instructor-test"),
]
