from django.conf import settings
from django.db import models

from courses.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    due_date = models.DateTimeField()

    total_marks = models.PositiveIntegerField()

    attachment = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )

    submission_file = models.FileField(
        upload_to="assignments/submissions/",
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    grade = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    feedback = models.TextField(
        blank=True,
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_student_assignment_submission",
            )
        ]

    def __str__(self):
        return f"{self.student.email} - {self.assignment.title}"
