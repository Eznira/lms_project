from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
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
    ExamAttempt,
    Examination,
    ExamQuestion,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)
from .permissions import (
    IsAssignmentOwnerOrAdmin,
    IsExamAttemptOwnerOrAdmin,
    IsExamOwnerOrAdmin,
    IsExamQuestionOwnerOrAdmin,
    IsQuizOwnerOrAdmin,
    IsQuizQuestionOwnerOrAdmin,
    IsSubmissionGraderOrAdmin,
    IsSubmissionOwnerOrAdmin,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    ExamAttemptSerializer,
    ExaminationSerializer,
    ExamQuestionSerializer,
    ExamSubmitSerializer,
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

        if user.role == user.Role.ADMIN:
            queryset = Quiz.objects.all()

        elif user.role == user.Role.INSTRUCTOR:
            queryset = Quiz.objects.filter(course__instructor=user)

        else:
            queryset = Quiz.objects.filter(
                course__status=Course.Status.PUBLISHED,
                course__enrollments__student=user,
            )

        # Optional course filter
        course_id = self.request.query_params.get("course")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset

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

    @action(
        detail=True,
        methods=["get"],
        url_path="questions",
    )
    def questions(self, request, pk=None):
        quiz = self.get_object()

        questions = QuizQuestion.objects.filter(quiz=quiz).order_by("order")

        serializer = QuizQuestionSerializer(
            questions,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


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

        serializer = BulkQuizQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz = serializer.validated_data["quiz"]

        if (
            request.user.role != request.user.Role.ADMIN
            and quiz.course.instructor != request.user
        ):
            return Response(
                {"detail": ("You can only add questions to your own quizzes.")},
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

    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            return QuizAttempt.objects.all()

        if user.role == user.Role.INSTRUCTOR:
            return QuizAttempt.objects.filter(quiz__course__instructor=user)

        return QuizAttempt.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        user = request.user

        # Only students can take quizzes
        if user.role != user.Role.STUDENT:
            return Response(
                {"detail": "Only students can attempt quizzes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        quiz_id = request.data.get("quiz")

        if not quiz_id:
            return Response(
                {"quiz": "Quiz ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get published quiz
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

        # Quiz must contain questions
        if not quiz.questions.exists():
            return Response(
                {"detail": "Quiz must contain at least one question."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Student must be enrolled
        if not quiz.course.enrollments.filter(student=user).exists():
            return Response(
                {"detail": "You must be enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Calculate total marks
        total_marks = sum(question.marks for question in quiz.questions.all())

        # Create a new attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=user,
            total_marks=total_marks,
        )

        serializer = self.get_serializer(attempt)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="submit",
    )
    def submit(self, request, pk=None):
        attempt = self.get_object()

        # Only the student who owns the attempt can submit it
        if attempt.student != request.user:
            return Response(
                {"detail": "You can only submit your own attempt."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevent submitting twice
        if attempt.submitted_at:
            return Response(
                {"detail": "This attempt has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check time limit
        now = timezone.now()

        deadline = attempt.started_at + timedelta(minutes=attempt.quiz.duration)

        if now > deadline:
            return Response(
                {"detail": "The quiz time limit has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = request.data.get("answers", {})

        if not isinstance(answers, dict):
            return Response(
                {"answers": "Answers must be an object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Automatically grade
        score = 0

        for question in attempt.quiz.questions.all():
            answer = answers.get(str(question.id))

            if answer and answer.upper() == question.correct_answer:
                score += question.marks

        # Save result
        attempt.answers = answers
        attempt.score = score
        attempt.submitted_at = now

        attempt.save(
            update_fields=[
                "answers",
                "score",
                "submitted_at",
            ]
        )

        serializer = self.get_serializer(attempt)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ExaminationViewSet(viewsets.ModelViewSet):
    serializer_class = ExaminationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            queryset = Examination.objects.all()

        elif user.role == user.Role.INSTRUCTOR:
            queryset = Examination.objects.filter(course__instructor=user)

        else:
            queryset = Examination.objects.filter(
                course__status=Course.Status.PUBLISHED,
                course__enrollments__student=user,
            )

        # Optional course filtering:
        # /api/examinations/?course=1
        course_id = self.request.query_params.get("course")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.distinct()

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
                IsExamOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied(
                "You can only create examinations for your own courses."
            )

        serializer.save()

    @action(
        detail=True,
        methods=["get"],
        url_path="questions",
    )
    def questions(self, request, pk=None):
        examination = self.get_object()

        questions = ExamQuestion.objects.filter(examination=examination).order_by(
            "order"
        )

        serializer = ExamQuestionSerializer(
            questions,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


class ExamQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            queryset = ExamQuestion.objects.all()

        elif user.role == user.Role.INSTRUCTOR:
            queryset = ExamQuestion.objects.filter(examination__course__instructor=user)

        else:
            queryset = ExamQuestion.objects.filter(
                examination__course__status=Course.Status.PUBLISHED,
                examination__course__enrollments__student=user,
            )

        examination_id = self.request.query_params.get("examination")

        if examination_id:
            queryset = queryset.filter(examination_id=examination_id)

        return queryset.distinct()

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
                IsExamQuestionOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        examination = serializer.validated_data["examination"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and examination.course.instructor != self.request.user
        ):
            raise PermissionDenied(
                "You can only create questions for your own examinations."
            )

        serializer.save()


class ExamAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = ExamAttemptSerializer

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
            return ExamAttempt.objects.all()

        if user.role == user.Role.INSTRUCTOR:
            return ExamAttempt.objects.filter(examination__course__instructor=user)

        return ExamAttempt.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role != user.Role.STUDENT:
            return Response(
                {"detail": "Only students can attempt examinations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        examination_id = request.data.get("examination")

        if not examination_id:
            return Response(
                {"examination": "Examination ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            examination = Examination.objects.get(
                pk=examination_id,
                course__status=Course.Status.PUBLISHED,
            )

        except Examination.DoesNotExist:
            return Response(
                {"detail": "Examination not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Student must be enrolled
        if not examination.course.enrollments.filter(student=user).exists():
            return Response(
                {"detail": "You must be enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()

        # Exam hasn't started
        if now < examination.start_time:
            return Response(
                {"detail": "This examination has not started yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Exam has ended
        if now > examination.end_time:
            return Response(
                {"detail": "This examination has ended."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Must contain questions
        if not examination.questions.exists():
            return Response(
                {"detail": "Examination must contain at least one question."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_marks = sum(question.marks for question in examination.questions.all())

        attempt = ExamAttempt.objects.create(
            examination=examination,
            student=user,
            total_marks=total_marks,
        )

        serializer = self.get_serializer(attempt)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=ExamSubmitSerializer,
        responses=ExamAttemptSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="submit",
    )
    def submit(self, request, pk=None):
        attempt = self.get_object()

        # Only the student who owns the attempt can submit it
        if attempt.student != request.user:
            return Response(
                {"detail": "You can only submit your own attempt."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if attempt.submitted_at:
            return Response(
                {"detail": "This attempt has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        # Student's personal time limit
        attempt_deadline = attempt.started_at + timedelta(
            minutes=attempt.examination.duration
        )

        # The exam itself also has an end time.
        # The earlier deadline wins.
        deadline = min(
            attempt_deadline,
            attempt.examination.end_time,
        )

        if now > deadline:
            return Response(
                {"detail": "The examination time limit has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = request.data.get("answers", {})

        if not isinstance(answers, dict):
            return Response(
                {"answers": "Answers must be an object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score = 0

        for question in attempt.examination.questions.all():
            # Essay questions require manual grading
            if question.question_type == ExamQuestion.QuestionType.ESSAY:
                continue

            answer = answers.get(str(question.id))

            if answer and answer.upper() == question.correct_answer:
                score += question.marks

        attempt.answers = answers
        attempt.score = score
        attempt.submitted_at = now

        attempt.save(
            update_fields=[
                "answers",
                "score",
                "submitted_at",
            ]
        )

        serializer = self.get_serializer(attempt)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
