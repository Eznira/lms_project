from datetime import timedelta

from django.contrib.admin import action
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course
from courses.permissions import IsInstructorOrAdmin

from .models import (
    Assignment,
    AssignmentSubmission,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)
from .permissions import (
    IsAssignmentOwnerOrAdmin,
    IsQuizOwnerOrAdmin,
    IsQuizQuestionOwnerOrAdmin,
    IsSubmissionGraderOrAdmin,
    IsSubmissionOwnerOrAdmin,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    QuizAttemptSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Assignment.objects.filter(
                course__status=Course.Status.PUBLISHED,
                course__enrollments__student=user,
            )

        if user.role == user.Role.INSTRUCTOR:
            return Assignment.objects.filter(
                Q(course__instructor=user) | Q(course__status=Course.Status.PUBLISHED)
            )

        return Assignment.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
            ]

        if self.action in ["update", "partial_update", "destroy"]:
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
                IsAssignmentOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied(
                "You can only create assignments for your own courses."
            )

        serializer.save()

    def perform_update(self, serializer):
        course = serializer.validated_data.get(
            "course",
            serializer.instance.course,
        )

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied(
                "You can only assign assignments to your own courses."
            )

        serializer.save()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            return AssignmentSubmission.objects.all()

        if user.role == user.Role.STUDENT:
            return AssignmentSubmission.objects.filter(
                student=user,
            )

        return AssignmentSubmission.objects.filter(
            assignment__course__instructor=user,
        )

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action in ["retrieve", "list"]:
            return [
                IsAuthenticated(),
                IsSubmissionOwnerOrAdmin(),
            ]

        if self.action in ["update", "partial_update"]:
            return [
                IsAuthenticated(),
                IsSubmissionGraderOrAdmin(),
            ]

        if self.action == "destroy":
            return [
                IsAuthenticated(),
                IsSubmissionOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != user.Role.STUDENT:
            raise PermissionDenied("Only students can submit assignments.")

        assignment = serializer.validated_data["assignment"]

        if not assignment.course.enrollments.filter(student=user).exists():
            raise PermissionDenied("You must be enrolled in this course.")

        if AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=user,
        ).exists():
            raise PermissionDenied("You have already submitted this assignment.")

        serializer.save(student=user)


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Quiz.objects.filter(
                course__status=Course.Status.PUBLISHED,
                course__enrollments__student=user,
            )

        if user.role == user.Role.INSTRUCTOR:
            return Quiz.objects.filter(
                Q(course__instructor=user) | Q(course__status=Course.Status.PUBLISHED)
            )

        return Quiz.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
            ]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
                IsQuizOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied("You can only create quizzes for your own courses.")

        serializer.save()

    def perform_update(self, serializer):
        course = serializer.validated_data.get(
            "course",
            serializer.instance.course,
        )

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied("You can only assign quizzes to your own courses.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        quiz = self.get_object()

        if not quiz.questions.exists():
            return Response(
                {
                    "detail": (
                        "A quiz must contain at least one question "
                        "before it can be deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            return QuizQuestion.objects.all()

        if user.role == user.Role.INSTRUCTOR:
            return QuizQuestion.objects.filter(quiz__course__instructor=user)

        return QuizQuestion.objects.filter(
            quiz__course__status=Course.Status.PUBLISHED,
            quiz__course__enrollments__student=user,
        )

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
            ]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                IsInstructorOrAdmin(),
                IsQuizQuestionOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        quiz = serializer.validated_data["quiz"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and quiz.course.instructor != self.request.user
        ):
            raise PermissionDenied("You can only add questions to your own quizzes.")

        serializer.save()

        if request.user.role not in [
            request.user.Role.INSTRUCTOR,
            request.user.Role.ADMIN,
        ]:
            return Response(
                {"detail": "Only instructors and admins can add questions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BulkQuizQuestionSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        quiz = serializer.validated_data["quiz"]

        if (
            request.user.role != request.user.Role.ADMIN
            and quiz.course.instructor != request.user
        ):
            return Response(
                {
                    "detail": (
                        "You can only add questions to your own quizzes."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        questions = serializer.save()

        return Response(
            QuizQuestionSerializer(
                questions,
                many=True,
            ).data,
            status=status.HTTP_201_CREATED,
        )

class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            return QuizAttempt.objects.all()

        if user.role == user.Role.INSTRUCTOR:
            return QuizAttempt.objects.filter(quiz__course__instructor=user)

        return QuizAttempt.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role != user.Role.STUDENT:
            return Response(
                {"detail": "Only students can attempt quizzes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        quiz_id = request.data.get("quiz")

        try:
            quiz = Quiz.objects.get(
                pk=quiz_id,
                course__status=Course.Status.PUBLISHED,
            )
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Quiz not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not quiz.questions.exists():
            return Response(
                {"detail": "Quiz must contain at least one question."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not quiz.course.enrollments.filter(student=user).exists():
            return Response(
                {"detail": "You must be enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if QuizAttempt.objects.filter(
            quiz=quiz,
            student=user,
        ).exists():
            return Response(
                {"detail": "You have already attempted this quiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = request.data.get("answers", {})

        score = 0
        total_marks = 0

        for question in quiz.questions.all():
            total_marks += question.marks

            answer = answers.get(str(question.id))

            if answer and answer.upper() == question.correct_answer:
                score += question.marks

        now = timezone.now()

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=user,
            answers=answers,
            score=score,
            total_marks=total_marks,
            submitted_at=now,
        )

        serializer = self.get_serializer(attempt)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )