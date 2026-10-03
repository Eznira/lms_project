from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, settings
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .models import EmailVerificationToken
from .permissions import IsAdmin
from .serializers import (
    InstructorCreateSerializer,
    InstructorSetPasswordSerializer,
    LogoutRequestSerializer,
    LogoutResponseSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
)
from .services.email_service import EmailService

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register student",
        description="Register a new student account. Public registration always creates a STUDENT account and requires email verification before login.",
        request=RegisterSerializer,
        responses=OpenApiResponse(description="Registration confirmation containing the account email."),
        examples=[OpenApiExample("Register student", value={"email": "student@example.com", "first_name": "John", "last_name": "Doe", "password": "StrongPassword123!", "password_confirm": "StrongPassword123!"}, request_only=True)],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        verification_token = (
            user.verification_tokens.filter(expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )

        if verification_token:
            try:
                EmailService.send_verification_email(
            user=user,
            token=verification_token.token,
        )
            except Exception as e:
                print("EMAIL ERROR:", repr(e))
                raise

        return Response(
            {
                "detail": ("Registration successful. Please verify your email."),
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify email",
        description="Verify a user's email address using the UUID token delivered by email. A successful verification activates the account.",
        request=VerifyEmailSerializer,
        responses=OpenApiResponse(description="Email verification confirmation."),
        examples=[OpenApiExample("Verification token", value={"token": "00000000-0000-0000-0000-000000000000"}, request_only=True)],
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        token = get_object_or_404(
            EmailVerificationToken,
            token=serializer.validated_data["token"],
        )

        if token.is_expired():
            return Response(
                {"detail": "Verification token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user

        user.email_verified = True
        user.is_active = True

        user.save(
            update_fields=[
                "email_verified",
                "is_active",
            ]
        )

        token.delete()

        return Response({"detail": "Email verified successfully."})


class InstructorCreateView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        summary="Create instructor",
        description="Create an instructor account. This endpoint is restricted to administrators; the instructor receives a verification/setup token before first login.",
        request=InstructorCreateSerializer,
        responses=OpenApiResponse(description="Instructor creation confirmation and instructor details."),
        examples=[OpenApiExample("Create instructor", value={"email": "instructor@example.com", "first_name": "Jane", "last_name": "Smith", "qualification": "B.Sc. Computer Science", "specialization": "Backend Development", "biography": "Backend instructor.", "phone": "+2348000000000"}, request_only=True)],
    )
    def post(self, request):
        serializer = InstructorCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        instructor = serializer.save()

        verification_token = (
            instructor.verification_tokens.filter(expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )

        if verification_token:
            EmailService.send_verification_email(
                user=instructor,
                token=verification_token.token,
            )

        return Response(
            {
                "detail": ("Instructor created successfully. Verification email sent."),
                "instructor": {
                    "id": instructor.id,
                    "email": instructor.email,
                    "first_name": instructor.first_name,
                    "last_name": instructor.last_name,
                    "role": instructor.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class InstructorSetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Set instructor password",
        description="Complete instructor account setup using the verification token and create the password used for login.",
        request=InstructorSetPasswordSerializer,
        responses=OpenApiResponse(description="Password setup confirmation."),
        examples=[OpenApiExample("Set password", value={"token": "00000000-0000-0000-0000-000000000000", "password": "InstructorPass123!", "password_confirm": "InstructorPass123!"}, request_only=True)],
    )
    def post(self, request):
        serializer = InstructorSetPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        token = get_object_or_404(
            EmailVerificationToken,
            token=serializer.validated_data["token"],
        )

        if token.is_expired():
            return Response(
                {"detail": "Verification token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user

        if user.role != User.Role.INSTRUCTOR:
            return Response(
                {"detail": "This endpoint is only for instructors."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["password"])

        user.email_verified = True
        user.is_active = True

        user.save(
            update_fields=[
                "password",
                "email_verified",
                "is_active",
            ]
        )

        token.delete()

        return Response({"detail": "Password created successfully. You can now login."})

@extend_schema_view(
    post=extend_schema(
        request=TokenObtainPairSerializer,
        summary="Login",
        description="Authenticate a user and return access and refresh tokens.",
    )
)
class LoginView(TokenObtainPairView):
    pass
@extend_schema_view(
    post=extend_schema(
        summary="Refresh access token",
        description="Exchange a valid refresh token for a new access token.",
        request=TokenRefreshSerializer,
        responses=TokenRefreshSerializer,
        examples=[OpenApiExample("Refresh token", value={"refresh": "<refresh-token>"}, request_only=True)],
    )
)
class RefreshTokenView(TokenRefreshView):
    pass

class LogoutView(APIView):
    @extend_schema(
        summary="Logout",
        description="Blacklist the supplied refresh token so it can no longer be used to obtain access tokens.",
        request=LogoutRequestSerializer,
        responses=LogoutResponseSerializer,
        examples=[OpenApiExample("Logout", value={"refresh": "<refresh-token>"}, request_only=True)],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response({"detail": "Logout successful."})

        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request password reset",
        description="Request a password-reset email. The response does not reveal whether the supplied email belongs to an account.",
        request=PasswordResetRequestSerializer,
        responses=OpenApiResponse(description="Password reset request confirmation."),
        examples=[OpenApiExample("Password reset request", value={"email": "student@example.com"}, request_only=True)],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        # Don't reveal whether email exists.
        if user and user.is_active:
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            token = default_token_generator.make_token(user)

            reset_url = (
                f"{settings.BACKEND_URL}"
                f"/api/auth/password-reset-confirm/"
                f"?uid={uid}&token={token}"
            )

            EmailService.send_password_reset_email(
                user=user,
                uid=uid,
                token=token,
                reset_url=reset_url,
            )

        return Response(
            {
                "detail": "If an account exists with that email, "
                "a password reset link has been sent."
            }
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Confirm password reset",
        description="Set a new password using the UID and reset token from the password-reset link.",
        request=PasswordResetConfirmSerializer,
        responses=OpenApiResponse(description="Password reset confirmation."),
        examples=[OpenApiExample("Confirm reset", value={"uid": "encoded-uid", "token": "reset-token", "new_password": "NewStrongPassword123!", "new_password_confirm": "NewStrongPassword123!"}, request_only=True)],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))

            user = User.objects.get(pk=user_id)

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(
            user,
            token,
        ):
            return Response(
                {"detail": "Invalid or expired password reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])

        user.save(update_fields=["password"])

        return Response({"detail": "Password reset successful."})

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's account information and role-specific profile fields.",
        request=None,
        responses=ProfileSerializer,
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)

        return Response(serializer.data)

    @extend_schema(
        summary="Update user profile",
        description="Update editable account fields and role-specific profile information for the authenticated user.",
        request=ProfileSerializer,
        responses=ProfileSerializer,
    )
    def patch(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)
# # Test view to get the current logged-in user's information
# class MeView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response(
#             {
#                 "id": request.user.id,
#                 "username": request.user.username,
#                 "email": request.user.email,
#                 "role": request.user.role,
#             }
#         )


# # Test view for instructor permisssion
# class InstructorTestView(APIView):
#     permission_classes = [IsAuthenticated, IsInstructor]

#     def get(self, request):
#         return Response(
#             {
#                 "message": "Welcome, Instructor!",
#                 "user": request.user.username,
#             }
#         )
