from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from assessments.models import Assignment, Examination
from notifications.models import Notification
from notifications.services import NotificationService


class Command(BaseCommand):
    help = "Send reminders for upcoming assignments and examinations."

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_window = now + timedelta(days=1)

        self.send_assignment_reminders(
            now,
            reminder_window,
        )

        self.send_exam_reminders(
            now,
            reminder_window,
        )

        self.stdout.write(self.style.SUCCESS("Reminder processing completed."))

    def send_assignment_reminders(
        self,
        now,
        reminder_window,
    ):
        assignments = Assignment.objects.filter(
            due_date__gt=now,
            due_date__lte=reminder_window,
        ).select_related("course")

        for assignment in assignments:
            enrollments = assignment.course.enrollments.select_related("student")

            for enrollment in enrollments:
                student = enrollment.student

                already_sent = Notification.objects.filter(
                    recipient=student,
                    notification_type=(
                        Notification.NotificationType.ASSIGNMENT_REMINDER
                    ),
                    message__contains=assignment.title,
                ).exists()

                if already_sent:
                    continue

                NotificationService.assignment_reminder(
                    student=student,
                    assignment=assignment,
                )

                self.stdout.write(f"Assignment reminder sent to {student.email}")

    def send_exam_reminders(
        self,
        now,
        reminder_window,
    ):
        examinations = Examination.objects.filter(
            start_time__gt=now,
            start_time__lte=reminder_window,
            status=Examination.Status.SCHEDULED,
        ).select_related("course")

        for examination in examinations:
            enrollments = examination.course.enrollments.select_related("student")

            for enrollment in enrollments:
                student = enrollment.student

                already_sent = Notification.objects.filter(
                    recipient=student,
                    notification_type=(Notification.NotificationType.EXAM_REMINDER),
                    message__contains=examination.title,
                ).exists()

                if already_sent:
                    continue

                NotificationService.exam_reminder(
                    student=student,
                    examination=examination,
                )

                self.stdout.write(f"Exam reminder sent to {student.email}")
