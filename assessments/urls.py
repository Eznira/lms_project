from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentSubmissionViewSet,
    AssignmentViewSet,
    QuizAttemptViewSet,
    QuizQuestionViewSet,
    QuizViewSet,
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

urlpatterns = router.urls