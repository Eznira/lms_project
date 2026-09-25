from django.conf import settings
from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_email(
        *,
        subject,
        message,
        recipient,
    ):
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            using="default",
        )

    @staticmethod
    def send_verification_email(
        *,
        user,
        token,
    ):
        verification_url = (
            f"{settings.BACKEND_URL}/api/auth/verify-email/?token={token}"
        )

        EmailService.send_email(
            subject="Verify your LMS account",
            message=(
                f"Hello {user.first_name},\n\n"
                "Please verify your email address.\n\n"
                f"Verification token:\n{token}\n\n"
                f"Verification URL:\n{verification_url}\n\n"
                "This link expires in 24 hours."
            ),
            recipient=user.email,
        )

    @staticmethod
    def send_password_reset_email(
        *,
        user,
        uid,
        token,
        reset_url,
    ):
        EmailService.send_email(
            subject="Reset your LMS password",
            message=(
                f"Hello {user.first_name},\n\n"
                "Use the following information to reset your password.\n\n"
                f"UID: {uid}\n"
                f"Token: {token}\n\n"
                f"Reset URL:\n{reset_url}\n\n"
                "If you did not request this, ignore this email."
            ),
            recipient=user.email,
        )
