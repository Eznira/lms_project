from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ENROLLMENT = "ENROLLMENT", "Enrollment"
        ASSIGNMENT_SUBMISSION = (
            "ASSIGNMENT_SUBMISSION",
            "Assignment Submission",
        )
        EXAM_SUBMISSION = "EXAM_SUBMISSION", "Examination Submission"
        ASSIGNMENT_REMINDER = "ASSIGNMENT_REMINDER", "Assignment Reminder"
        EXAM_REMINDER = "EXAM_REMINDER", "Examination Reminder"
        GRADE = "GRADE", "Grade"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        GENERAL = "GENERAL", "General"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
