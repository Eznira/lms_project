from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(user, token):
    verification_url = f"http://127.0.0.1:8000/api/auth/verify-email/?token={token}"

    send_mail(
        subject="Verify your LMS account",
        message=(
            f"Hello {user.first_name},\n\n"
            f"Please verify your email address.\n\n"
            f"Verification token:\n"
            f"{token}\n\n"
            f"Verification URL:\n"
            f"{verification_url}\n\n"
            f"This link expires in 24 hours."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
