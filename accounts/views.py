from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerificationToken
from .permissions import IsAdmin
from .serializers import (
    InstructorCreateSerializer,
    InstructorSetPasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
)
from .utils import send_verification_email

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

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
            send_verification_email(
                user,
                verification_token.token,
            )

        return Response(
            {
                "detail": ("Registration successful. Please verify your email."),
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

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
            send_verification_email(
                instructor,
                verification_token.token,
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


class LogoutView(APIView):
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
                "http://127.0.0.1:8000/"
                f"api/auth/password-reset-confirm/"
                f"?uid={uid}&token={token}"
            )

            send_mail(
                subject="Reset your LMS password",
                message=(
                    f"Hello {user.first_name},\n\n"
                    f"Use the following information "
                    f"to reset your password.\n\n"
                    f"UID: {uid}\n"
                    f"Token: {token}\n\n"
                    f"Reset URL:\n{reset_url}\n\n"
                    f"If you did not request this, "
                    f"ignore this email."
                ),
                from_email="noreply@lms.local",
                recipient_list=[user.email],
            )

        return Response(
            {
                "detail": "If an account exists with that email, "
                "a password reset link has been sent."
            }
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

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
