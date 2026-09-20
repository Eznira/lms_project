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


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class QuizQuestion(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple Choice"
        TRUE_FALSE = "TRUE_FALSE", "True / False"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
    )

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(
        max_length=255,
        blank=True,
    )
    option_d = models.CharField(
        max_length=255,
        blank=True,
    )

    correct_answer = models.CharField(max_length=1)

    marks = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "order"],
                name="unique_question_order_per_quiz",
            )
        ]

    def __str__(self):
        return self.question_text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )

    answers = models.JSONField(default=dict)

    score = models.PositiveIntegerField(default=0)

    total_marks = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "student"],
                name="unique_student_quiz_attempt",
            )
        ]

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title}"