from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course
from courses.permissions import IsInstructorOrAdmin

from .models import Assignment, AssignmentSubmission
from .permissions import (
    IsAssignmentOwnerOrAdmin,
    IsSubmissionGraderOrAdmin,
    IsSubmissionOwnerOrAdmin,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
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
