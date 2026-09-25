from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentSubmissionViewSet,
    AssignmentViewSet,
    CertificateViewSet,
    ExamAttemptViewSet,
    ExaminationViewSet,
    ExamQuestionViewSet,
    GradeViewSet,
    QuizAttemptViewSet,
    QuizQuestionViewSet,
    QuizViewSet,
    ResultViewSet,
)

router = DefaultRouter()

router.register(
    "assignments",
    AssignmentViewSet,
    basename="assignment",
)

router.register(
    "submissions",
    AssignmentSubmissionViewSet,
    basename="submission",
)

router.register(
    "quizzes",
    QuizViewSet,
    basename="quiz",
)

router.register(
    "quiz-questions",
    QuizQuestionViewSet,
    basename="quiz-question",
)

router.register(
    "quiz-attempts",
    QuizAttemptViewSet,
    basename="quiz-attempt",
)

router.register(
    "examinations",
    ExaminationViewSet,
    basename="examination",
)

router.register(
    "exam-questions",
    ExamQuestionViewSet,
    basename="exam-question",
)

router.register(
    "exam-attempts",
    ExamAttemptViewSet,
    basename="exam-attempt",
)

router.register(
    "grades",
    GradeViewSet,
    basename="grade",
)

router.register(
    "results",
    ResultViewSet,
    basename="result",
)

router.register(
    "certificates",
    CertificateViewSet,
    basename="certificate",
)

urlpatterns = router.urls