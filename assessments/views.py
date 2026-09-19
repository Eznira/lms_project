from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assessments.permissions import IsAssignmentOwnerOrAdmin
from courses.models import Course
from courses.permissions import IsCourseOwnerOrAdmin, IsInstructorOrAdmin

from .models import Assignment
from .serializers import AssignmentSerializer


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
