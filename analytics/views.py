from django.db.models import Avg, Count, Q, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from analytics.serializers import (
    AdminAnalyticsSerializer,
    InstructorAnalyticsSerializer,
    StudentAnalyticsSerializer,
)
from assessments.models import (
    Assignment,
    AssignmentSubmission,
    Certificate,
    ExamAttempt,
    QuizAttempt,
)
from courses.models import Course, Lesson
from enrollments.models import Enrollment, LessonCompletion
from reviews.models import Review


def percentage(score, total):
    """
    Calculate a percentage safely.
    """
    if not total:
        return 0

    return round((score / total) * 100, 2)


class StudentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get student analytics",
        description="Return analytics data for the authenticated student.",
        responses=StudentAnalyticsSerializer,
    )
    def get(self, request):
        user = request.user

        if user.role != User.Role.STUDENT:
            return Response(
                {"detail": ("Only students can access student analytics.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        enrollments = Enrollment.objects.filter(
            student=user,
        )

        courses = Course.objects.filter(
            enrollments__student=user,
        ).distinct()

        certificates = Certificate.objects.filter(
            student=user,
        )

        # --------------------------------------------------
        # Courses
        # --------------------------------------------------

        courses_enrolled = courses.count()

        completed_courses = certificates.count()

        # --------------------------------------------------
        # Lessons / Learning Progress
        # --------------------------------------------------

        completed_lessons = LessonCompletion.objects.filter(
            student=user,
        ).count()

        total_lessons = Lesson.objects.filter(
            course__in=courses,
        ).count()

        learning_progress = percentage(
            completed_lessons,
            total_lessons,
        )

        # Course-by-course progress
        course_progress = []

        for course in courses:
            total_course_lessons = course.lessons.count()

            completed_course_lessons = LessonCompletion.objects.filter(
                student=user,
                lesson__course=course,
            ).count()

            course_progress.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "lessons_completed": completed_course_lessons,
                    "total_lessons": total_course_lessons,
                    "progress_percentage": percentage(
                        completed_course_lessons,
                        total_course_lessons,
                    ),
                    "completed": certificates.filter(
                        course=course,
                    ).exists(),
                }
            )

        # --------------------------------------------------
        # Assignments
        # --------------------------------------------------

        assignment_submissions = AssignmentSubmission.objects.filter(
            student=user,
        ).select_related("assignment")

        graded_assignments = assignment_submissions.filter(
            grade__isnull=False,
        )

        assignment_scores = []

        for submission in graded_assignments:
            assignment_scores.append(
                {
                    "assignment_id": submission.assignment.id,
                    "assignment_title": submission.assignment.title,
                    "score": submission.grade,
                    "total_marks": submission.assignment.total_marks,
                    "percentage": percentage(
                        submission.grade,
                        submission.assignment.total_marks,
                    ),
                }
            )

        # --------------------------------------------------
        # Quizzes
        # --------------------------------------------------

        quiz_attempts = QuizAttempt.objects.filter(
            student=user,
            submitted_at__isnull=False,
        ).select_related("quiz")

        quiz_performance = []

        for attempt in quiz_attempts:
            quiz_performance.append(
                {
                    "quiz_id": attempt.quiz.id,
                    "quiz_title": attempt.quiz.title,
                    "score": attempt.score,
                    "total_marks": attempt.total_marks,
                    "percentage": percentage(
                        attempt.score,
                        attempt.total_marks,
                    ),
                    "submitted_at": attempt.submitted_at,
                }
            )

        average_quiz_percentage = (
            round(
                sum(item["percentage"] for item in quiz_performance)
                / len(quiz_performance),
                2,
            )
            if quiz_performance
            else 0
        )

        # --------------------------------------------------
        # Certificates
        # --------------------------------------------------

        certificates_earned = certificates.count()

        return Response(
            {
                "courses_enrolled": courses_enrolled,
                "completed_courses": completed_courses,
                "lessons_completed": completed_lessons,
                "total_lessons": total_lessons,
                "learning_progress": learning_progress,
                "course_progress": course_progress,
                "assignment_scores": assignment_scores,
                "quiz_performance": {
                    "total_attempts": len(quiz_performance),
                    "average_percentage": average_quiz_percentage,
                    "attempts": quiz_performance,
                },
                "certificates_earned": certificates_earned,
            }
        )


class InstructorAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get instructor analytics",
        description="Return analytics data for the authenticated instructor.",
        responses=InstructorAnalyticsSerializer
    )
    def get(self, request):
        user = request.user

        if user.role != User.Role.INSTRUCTOR:
            return Response(
                {"detail": ("Only instructors can access instructor analytics.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        courses = Course.objects.filter(
            instructor=user,
        )

        # --------------------------------------------------
        # Students
        # --------------------------------------------------

        total_students = (
            Enrollment.objects.filter(
                course__in=courses,
            )
            .values(
                "student",
            )
            .distinct()
            .count()
        )

        # --------------------------------------------------
        # Assignment Completion
        # --------------------------------------------------

        total_assignments = Assignment.objects.filter(
            course__in=courses,
        ).count()

        total_submissions = AssignmentSubmission.objects.filter(
            assignment__course__in=courses,
        ).count()

        graded_submissions = AssignmentSubmission.objects.filter(
            assignment__course__in=courses,
            grade__isnull=False,
        )

        assignment_completion_rate = (
            round(
                (
                    total_submissions
                    / (
                        Enrollment.objects.filter(
                            course__in=courses,
                        ).count()
                        * total_assignments
                    )
                )
                * 100,
                2,
            )
            if total_assignments
            and Enrollment.objects.filter(
                course__in=courses,
            ).exists()
            else 0
        )

        # --------------------------------------------------
        # Quiz Performance
        # --------------------------------------------------

        quiz_attempts = QuizAttempt.objects.filter(
            quiz__course__in=courses,
            submitted_at__isnull=False,
        )

        quiz_percentages = [
            percentage(
                attempt.score,
                attempt.total_marks,
            )
            for attempt in quiz_attempts
        ]

        average_quiz_performance = (
            round(
                sum(quiz_percentages) / len(quiz_percentages),
                2,
            )
            if quiz_percentages
            else 0
        )

        # --------------------------------------------------
        # Course Ratings
        # --------------------------------------------------

        average_course_rating = Review.objects.filter(
            course__in=courses,
        ).aggregate(
            average=Avg("rating"),
        )["average"]

        # --------------------------------------------------
        # Course Completion Statistics
        # --------------------------------------------------

        course_completion = []

        for course in courses:
            enrolled_students = Enrollment.objects.filter(
                course=course,
            ).count()

            completed_students = Certificate.objects.filter(
                course=course,
            ).count()

            course_completion.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "enrolled_students": enrolled_students,
                    "completed_students": completed_students,
                    "completion_rate": percentage(
                        completed_students,
                        enrolled_students,
                    ),
                }
            )

        return Response(
            {
                "total_students": total_students,
                "assignment_completion": {
                    "total_assignments": total_assignments,
                    "total_submissions": total_submissions,
                    "graded_submissions": graded_submissions.count(),
                    "completion_rate": assignment_completion_rate,
                },
                "quiz_performance": {
                    "total_attempts": quiz_attempts.count(),
                    "average_percentage": (average_quiz_performance),
                },
                "average_course_rating": (
                    round(average_course_rating, 2)
                    if average_course_rating is not None
                    else 0
                ),
                "course_completion_statistics": (course_completion),
            }
        )


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get admin analytics",
        description="Return analytics data for the authenticated admin.",
        responses=AdminAnalyticsSerializer
    )
    def get(self, request):
        user = request.user

        if user.role != User.Role.ADMIN:
            return Response(
                {"detail": ("Only admins can access admin analytics.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------
        # Users
        # --------------------------------------------------

        total_students = User.objects.filter(
            role=User.Role.STUDENT,
        ).count()

        total_instructors = User.objects.filter(
            role=User.Role.INSTRUCTOR,
        ).count()

        # --------------------------------------------------
        # Courses
        # --------------------------------------------------

        total_courses = Course.objects.count()

        # --------------------------------------------------
        # Active Enrollments
        #
        # An enrollment is considered active when the student
        # has not completed the course.
        # --------------------------------------------------

        total_enrollments = Enrollment.objects.count()

        completed_enrollments = (
            Certificate.objects.values(
                "student",
                "course",
            )
            .distinct()
            .count()
        )

        active_enrollments = max(
            total_enrollments - completed_enrollments,
            0,
        )

        # --------------------------------------------------
        # Course Completion Rates
        # --------------------------------------------------

        course_completion_rates = []

        for course in Course.objects.all():
            enrolled_students = Enrollment.objects.filter(
                course=course,
            ).count()

            completed_students = Certificate.objects.filter(
                course=course,
            ).count()

            course_completion_rates.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "enrolled_students": enrolled_students,
                    "completed_students": completed_students,
                    "completion_rate": percentage(
                        completed_students,
                        enrolled_students,
                    ),
                }
            )

        # --------------------------------------------------
        # Most Popular Courses
        # --------------------------------------------------

        popular_courses = Course.objects.annotate(
            enrollment_count=Count(
                "enrollments",
                distinct=True,
            )
        ).order_by("-enrollment_count", "title")[:5]

        most_popular_courses = [
            {
                "course_id": course.id,
                "course_title": course.title,
                "enrollment_count": course.enrollment_count,
            }
            for course in popular_courses
        ]

        # --------------------------------------------------
        # Student Engagement
        #
        # A student is considered engaged if they have at
        # least one learning activity.
        # --------------------------------------------------

        engaged_students = (
            User.objects.filter(
                role=User.Role.STUDENT,
            )
            .filter(
                Q(lesson_completions__isnull=False)
                | Q(assignment_submissions__isnull=False)
                | Q(quiz_attempts__submitted_at__isnull=False)
                | Q(exam_attempts__submitted_at__isnull=False)
            )
            .distinct()
            .count()
        )

        student_engagement_rate = percentage(
            engaged_students,
            total_students,
        )

        total_lesson_completions = LessonCompletion.objects.count()

        total_assignment_submissions = AssignmentSubmission.objects.count()

        total_quiz_attempts = QuizAttempt.objects.filter(
            submitted_at__isnull=False,
        ).count()

        total_exam_attempts = ExamAttempt.objects.filter(
            submitted_at__isnull=False,
        ).count()

        # --------------------------------------------------
        # Revenue
        #
        # This is enrollment-based revenue, because the
        # current LMS does not have a payment/transaction
        # model.
        # --------------------------------------------------

        revenue = Enrollment.objects.aggregate(
            total=Sum("course__price"),
        )["total"]

        paid_course_revenue = Enrollment.objects.filter(
            course__price__gt=0,
        ).aggregate(
            total=Sum("course__price"),
        )["total"]

        # --------------------------------------------------
        # Reviews
        # --------------------------------------------------

        average_course_rating = Review.objects.aggregate(
            average=Avg("rating"),
        )["average"]

        return Response(
            {
                "users": {
                    "total_students": total_students,
                    "total_instructors": total_instructors,
                },
                "courses": {
                    "total_courses": total_courses,
                    "course_completion_rates": (course_completion_rates),
                    "most_popular_courses": (most_popular_courses),
                },
                "enrollments": {
                    "total_enrollments": total_enrollments,
                    "active_enrollments": active_enrollments,
                    "completed_enrollments": (completed_enrollments),
                },
                "student_engagement": {
                    "engaged_students": engaged_students,
                    "engagement_rate": (student_engagement_rate),
                    "lesson_completions": (total_lesson_completions),
                    "assignment_submissions": (total_assignment_submissions),
                    "quiz_attempts": total_quiz_attempts,
                    "exam_attempts": total_exam_attempts,
                },
            
                "average_course_rating": (
                    round(average_course_rating, 2)
                    if average_course_rating is not None
                    else 0
                ),
            }
        )