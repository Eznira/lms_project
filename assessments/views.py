from datetime import timedelta

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
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
    Certificate,
    ExamAttempt,
    Examination,
    ExamQuestion,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)
from .permissions import (
    IsAssignmentOwnerOrAdmin,
    IsCertificateOwnerOrAdmin,
    IsExamAttemptOwnerOrAdmin,
    IsExamOwnerOrAdmin,
    IsExamQuestionOwnerOrAdmin,
    IsInstructorOrAdminCanGrade,
    IsQuizOwnerOrAdmin,
    IsQuizQuestionOwnerOrAdmin,
    IsSubmissionGraderOrAdmin,
    IsSubmissionOwnerOrAdmin,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    CertificateSerializer,
    ExamAttemptSerializer,
    ExamGradeSerializer,
    ExaminationSerializer,
    ExamQuestionSerializer,
    ExamSubmitSerializer,
    GradeSerializer,
    QuizAttemptSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
    QuizSubmitSerializer,
    ResultSerializer,
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

    @extend_schema(
        request=QuizSubmitSerializer,
        responses=QuizAttemptSerializer,
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
        "patch",
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

    def get_permissions(self):
        if self.action == "submit":
            return [
                IsAuthenticated(),
                IsExamAttemptOwnerOrAdmin(),
            ]

        if self.action == "grade":
            return [
                IsAuthenticated(),
                IsInstructorOrAdminCanGrade(),
            ]

        return [IsAuthenticated()]

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

    @extend_schema(
        request=ExamGradeSerializer,
        responses=ExamAttemptSerializer,
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="grade",
    )
    def grade(self, request, pk=None):
        attempt = self.get_object()

        # Exam must already be submitted
        if not attempt.submitted_at:
            return Response(
                {"detail": "You cannot grade an exam that has not been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate grading request
        serializer = ExamGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data["question_id"]
        marks = serializer.validated_data["marks"]

        # Make sure question belongs to this examination
        try:
            question = ExamQuestion.objects.get(
                id=question_id,
                examination=attempt.examination,
            )
        except ExamQuestion.DoesNotExist:
            return Response(
                {"detail": "Question does not belong to this examination."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only essay questions require manual grading
        if question.question_type != ExamQuestion.QuestionType.ESSAY:
            return Response(
                {"detail": "Only essay questions require manual grading."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cannot award more than the question's marks
        if marks > question.marks:
            return Response(
                {"marks": f"Marks cannot exceed {question.marks}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save the manual grade
        manual_grades = attempt.manual_grades or {}

        manual_grades[str(question.id)] = marks

        attempt.manual_grades = manual_grades

        # Recalculate the complete score
        score = 0

        for exam_question in attempt.examination.questions.all():
            # Automatically graded questions
            if exam_question.question_type in [
                ExamQuestion.QuestionType.MCQ,
                ExamQuestion.QuestionType.TRUE_FALSE,
            ]:
                answer = attempt.answers.get(str(exam_question.id))

                if answer and answer.upper() == exam_question.correct_answer:
                    score += exam_question.marks

            # Manually graded essay questions
            elif exam_question.question_type == ExamQuestion.QuestionType.ESSAY:
                score += manual_grades.get(
                    str(exam_question.id),
                    0,
                )

        attempt.score = score

        attempt.save(
            update_fields=[
                "manual_grades",
                "score",
            ]
        )

        # Return updated attempt/result
        response_serializer = ExamAttemptSerializer(attempt)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

class GradeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List grades",
        description=(
            "Returns grades for assignments, quizzes, and examinations. "
            "Students see their own grades. Instructors see grades for "
            "students in their courses. Admins see all grades. "
            "For quizzes and examinations, only the highest submitted "
            "attempt per student and assessment is included."
        ),
        parameters=[
            OpenApiParameter(
                name="course",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter grades by course ID.",
            ),
        ],
        responses=GradeSerializer(many=True),
    )
    def list(self, request):
        user = request.user
        course_id = request.query_params.get("course")

        grades = []

        # =========================================================
        # ASSIGNMENTS
        # =========================================================

        if user.role == user.Role.STUDENT:
            assignment_submissions = AssignmentSubmission.objects.filter(
                student=user,
                grade__isnull=False,
            ).select_related(
                "assignment",
                "assignment__course",
            )

        elif user.role == user.Role.INSTRUCTOR:
            assignment_submissions = AssignmentSubmission.objects.filter(
                assignment__course__instructor=user,
                grade__isnull=False,
            ).select_related(
                "assignment",
                "assignment__course",
                "student",
            )

        else:
            assignment_submissions = AssignmentSubmission.objects.filter(
                grade__isnull=False,
            ).select_related(
                "assignment",
                "assignment__course",
                "student",
            )

        if course_id:
            assignment_submissions = assignment_submissions.filter(
                assignment__course_id=course_id
            )

        for submission in assignment_submissions:
            total_marks = submission.assignment.total_marks

            percentage = (
                round((submission.grade / total_marks) * 100, 2) if total_marks else 0
            )

            grades.append(
                {
                    "assessment_type": "ASSIGNMENT",
                    "assessment_id": submission.id,
                    "title": submission.assignment.title,
                    "score": submission.grade,
                    "total_marks": total_marks,
                    "percentage": percentage,
                }
            )

        # =========================================================
        # QUIZZES
        # =========================================================

        if user.role == user.Role.STUDENT:
            quiz_attempts = QuizAttempt.objects.filter(
                student=user,
                submitted_at__isnull=False,
            ).select_related(
                "quiz",
                "quiz__course",
            )

        elif user.role == user.Role.INSTRUCTOR:
            quiz_attempts = QuizAttempt.objects.filter(
                quiz__course__instructor=user,
                submitted_at__isnull=False,
            ).select_related(
                "quiz",
                "quiz__course",
                "student",
            )

        else:
            quiz_attempts = QuizAttempt.objects.filter(
                submitted_at__isnull=False,
            ).select_related(
                "quiz",
                "quiz__course",
                "student",
            )

        if course_id:
            quiz_attempts = quiz_attempts.filter(quiz__course_id=course_id)

        # ---------------------------------------------------------
        # Only the highest attempt for each student + quiz counts
        # ---------------------------------------------------------

        best_quiz_attempts = {}

        for attempt in quiz_attempts:
            key = (
                attempt.student_id,
                attempt.quiz_id,
            )

            current_best = best_quiz_attempts.get(key)

            if current_best is None or attempt.score > current_best.score:
                best_quiz_attempts[key] = attempt

        for attempt in best_quiz_attempts.values():
            total_marks = attempt.total_marks

            percentage = (
                round((attempt.score / total_marks) * 100, 2) if total_marks else 0
            )

            grades.append(
                {
                    "assessment_type": "QUIZ",
                    "assessment_id": attempt.id,
                    "title": attempt.quiz.title,
                    "score": attempt.score,
                    "total_marks": total_marks,
                    "percentage": percentage,
                }
            )

        # =========================================================
        # EXAMINATIONS
        # =========================================================

        if user.role == user.Role.STUDENT:
            exam_attempts = ExamAttempt.objects.filter(
                student=user,
                submitted_at__isnull=False,
            ).select_related(
                "examination",
                "examination__course",
            )

        elif user.role == user.Role.INSTRUCTOR:
            exam_attempts = ExamAttempt.objects.filter(
                examination__course__instructor=user,
                submitted_at__isnull=False,
            ).select_related(
                "examination",
                "examination__course",
                "student",
            )

        else:
            exam_attempts = ExamAttempt.objects.filter(
                submitted_at__isnull=False,
            ).select_related(
                "examination",
                "examination__course",
                "student",
            )

        if course_id:
            exam_attempts = exam_attempts.filter(examination__course_id=course_id)

        # ---------------------------------------------------------
        # Only the highest attempt for each student + examination
        # counts
        # ---------------------------------------------------------

        best_exam_attempts = {}

        for attempt in exam_attempts:
            key = (
                attempt.student_id,
                attempt.examination_id,
            )

            current_best = best_exam_attempts.get(key)

            if current_best is None or attempt.score > current_best.score:
                best_exam_attempts[key] = attempt

        for attempt in best_exam_attempts.values():
            total_marks = attempt.total_marks

            percentage = (
                round((attempt.score / total_marks) * 100, 2) if total_marks else 0
            )

            grades.append(
                {
                    "assessment_type": "EXAMINATION",
                    "assessment_id": attempt.id,
                    "title": attempt.examination.title,
                    "score": attempt.score,
                    "total_marks": total_marks,
                    "percentage": percentage,
                }
            )

        serializer = GradeSerializer(
            grades,
            many=True,
        )

        return Response(serializer.data)

class ResultViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List course results",
        description=(
            "Returns calculated course results. "
            "Students receive their own results. "
            "Instructors receive results for students associated with "
            "their courses. Admins receive results for all courses."
        ),
        parameters=[
            OpenApiParameter(
                name="course",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter results by course ID.",
            ),
        ],
        responses=ResultSerializer(many=True),
    )
    def list(self, request):
        user = request.user
        course_id = request.query_params.get("course")

        # =========================================================
        # DETERMINE COURSES
        # =========================================================

        if user.role == user.Role.STUDENT:
            courses = Course.objects.filter(enrollments__student=user)

        elif user.role == user.Role.INSTRUCTOR:
            courses = Course.objects.filter(instructor=user)

        else:
            courses = Course.objects.all()

        if course_id:
            courses = courses.filter(id=course_id)

        courses = courses.distinct()

        results = []

        # =========================================================
        # STUDENTS
        # =========================================================

        if user.role == user.Role.STUDENT:
            for course in courses:
                result = self.calculate_student_result(
                    student=user,
                    course=course,
                )

                results.append(result)

        # =========================================================
        # INSTRUCTORS / ADMINS
        # =========================================================

        else:
            for course in courses:
                # Get students who have activity in this course.
                student_ids = set()

                assignment_students = AssignmentSubmission.objects.filter(
                    assignment__course=course,
                ).values_list(
                    "student_id",
                    flat=True,
                )

                quiz_students = QuizAttempt.objects.filter(
                    quiz__course=course,
                ).values_list(
                    "student_id",
                    flat=True,
                )

                exam_students = ExamAttempt.objects.filter(
                    examination__course=course,
                ).values_list(
                    "student_id",
                    flat=True,
                )

                student_ids.update(assignment_students)
                student_ids.update(quiz_students)
                student_ids.update(exam_students)

                # -------------------------------------------------
                # Also include enrolled students
                # -------------------------------------------------

                enrolled_students = course.enrollments.values_list(
                    "student_id",
                    flat=True,
                )

                student_ids.update(enrolled_students)

                for student_id in student_ids:
                    from accounts.models import User

                    student = User.objects.get(id=student_id)

                    result = self.calculate_student_result(
                        student=student,
                        course=course,
                    )

                    results.append(result)

        serializer = ResultSerializer(
            results,
            many=True,
        )

        return Response(serializer.data)

    # =============================================================
    # CALCULATE ONE STUDENT'S RESULT FOR ONE COURSE
    # =============================================================

    def calculate_student_result(self, student, course):

        # =========================================================
        # ASSIGNMENTS
        # =========================================================

        assignment_submissions = AssignmentSubmission.objects.filter(
            assignment__course=course,
            student=student,
            grade__isnull=False,
        ).select_related(
            "assignment",
        )

        assignment_score = sum(
            submission.grade for submission in assignment_submissions
        )

        assignment_total = sum(
            submission.assignment.total_marks for submission in assignment_submissions
        )

        # =========================================================
        # QUIZZES
        # =========================================================

        quiz_attempts = QuizAttempt.objects.filter(
            quiz__course=course,
            student=student,
            submitted_at__isnull=False,
        )

        best_quiz_attempts = {}

        for attempt in quiz_attempts:
            current_best = best_quiz_attempts.get(attempt.quiz_id)

            if current_best is None or attempt.score > current_best.score:
                best_quiz_attempts[attempt.quiz_id] = attempt

        quiz_score = sum(attempt.score for attempt in best_quiz_attempts.values())

        quiz_total = sum(attempt.total_marks for attempt in best_quiz_attempts.values())

        # =========================================================
        # EXAMINATIONS
        # =========================================================

        exam_attempts = ExamAttempt.objects.filter(
            examination__course=course,
            student=student,
            submitted_at__isnull=False,
        )

        best_exam_attempts = {}

        for attempt in exam_attempts:
            current_best = best_exam_attempts.get(attempt.examination_id)

            if current_best is None or attempt.score > current_best.score:
                best_exam_attempts[attempt.examination_id] = attempt

        examination_score = sum(
            attempt.score for attempt in best_exam_attempts.values()
        )

        examination_total = sum(
            attempt.total_marks for attempt in best_exam_attempts.values()
        )

        # =========================================================
        # OVERALL RESULT
        # =========================================================

        total_score = assignment_score + quiz_score + examination_score

        total_marks = assignment_total + quiz_total + examination_total

        percentage = (
            round(
                (total_score / total_marks) * 100,
                2,
            )
            if total_marks
            else 0
        )

        return {
            "student_id": student.id,
            "student_email": student.email,
            "course_id": course.id,
            "course_title": course.title,
            "assignment_score": assignment_score,
            "assignment_total": assignment_total,
            "quiz_score": quiz_score,
            "quiz_total": quiz_total,
            "examination_score": examination_score,
            "examination_total": examination_total,
            "total_score": total_score,
            "total_marks": total_marks,
            "percentage": percentage,
        }

class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Certificate.objects.filter(student=user).select_related(
                "student",
                "course",
            )

        if user.role == user.Role.INSTRUCTOR:
            return Certificate.objects.filter(course__instructor=user).select_related(
                "student",
                "course",
            )

        return Certificate.objects.all().select_related(
            "student",
            "course",
        )

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
            ]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                IsCertificateOwnerOrAdmin(),
            ]

        return [
            IsAuthenticated(),
        ]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            raise PermissionDenied("Students cannot create certificates.")

        student = serializer.validated_data["student"]
        course = serializer.validated_data["course"]

        # Instructor can only issue certificates
        # for their own courses.
        if user.role == user.Role.INSTRUCTOR and course.instructor != user:
            raise PermissionDenied(
                "You can only issue certificates for your own courses."
            )

        # Calculate the student's current result.
        result = self.calculate_completion_percentage(
            student,
            course,
        )

        if result is None:
            raise PermissionDenied("The student has no graded work for this course.")

        try:
            serializer.save(completion_percentage=result)
        except IntegrityError:
            raise PermissionDenied(
                "This student already has a certificate for this course."
            )

    def calculate_completion_percentage(
        self,
        student,
        course,
    ):
        """
        Calculate the student's overall course percentage.

        Quiz and examination attempts:
        only the highest submitted attempt counts.
        """

        # =========================================================
        # ASSIGNMENTS
        # =========================================================

        assignment_submissions = AssignmentSubmission.objects.filter(
            assignment__course=course,
            student=student,
            grade__isnull=False,
        ).select_related("assignment")

        assignment_score = sum(
            submission.grade for submission in assignment_submissions
        )

        assignment_total = sum(
            submission.assignment.total_marks for submission in assignment_submissions
        )

        # =========================================================
        # QUIZZES
        # =========================================================

        quiz_attempts = QuizAttempt.objects.filter(
            quiz__course=course,
            student=student,
            submitted_at__isnull=False,
        )

        best_quiz_attempts = {}

        for attempt in quiz_attempts:
            current_best = best_quiz_attempts.get(attempt.quiz_id)

            if current_best is None or attempt.score > current_best.score:
                best_quiz_attempts[attempt.quiz_id] = attempt

        quiz_score = sum(attempt.score for attempt in best_quiz_attempts.values())

        quiz_total = sum(attempt.total_marks for attempt in best_quiz_attempts.values())

        # =========================================================
        # EXAMINATIONS
        # =========================================================

        exam_attempts = ExamAttempt.objects.filter(
            examination__course=course,
            student=student,
            submitted_at__isnull=False,
        )

        best_exam_attempts = {}

        for attempt in exam_attempts:
            current_best = best_exam_attempts.get(attempt.examination_id)

            if current_best is None or attempt.score > current_best.score:
                best_exam_attempts[attempt.examination_id] = attempt

        examination_score = sum(
            attempt.score for attempt in best_exam_attempts.values()
        )

        examination_total = sum(
            attempt.total_marks for attempt in best_exam_attempts.values()
        )

        # =========================================================
        # FINAL PERCENTAGE
        # =========================================================

        total_score = assignment_score + quiz_score + examination_score

        total_marks = assignment_total + quiz_total + examination_total

        if total_marks == 0:
            return None

        return round(
            (total_score / total_marks) * 100,
            2,
        )