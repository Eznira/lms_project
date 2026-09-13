from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import Category, Course, Lesson
from .permissions import (
    IsCourseOwnerOrAdmin,
    IsInstructorOrAdmin,
    IsLessonOwnerOrAdmin,
)
from .serializers import CategorySerializer, CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Course.objects.filter(status=Course.Status.PUBLISHED)
        if user.role == user.Role.INSTRUCTOR:
            return Course.objects.filter(Q(instructor=user) | Q(status=Course.Status.PUBLISHED) )

        return Course.objects.all()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [
                IsAuthenticated,
                IsInstructorOrAdmin,
            ]

        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [
                IsAuthenticated,
                IsInstructorOrAdmin,
                IsCourseOwnerOrAdmin,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy"
        ]: return [IsAuthenticated(), IsAdmin()]

        return [IsAuthenticated()]

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Lesson.objects.filter(course__status=Course.Status.PUBLISHED)

        if user.role == user.Role.INSTRUCTOR:
            return Lesson.objects.filter(
                Q(course__instructor=user) | Q(course__status=Course.Status.PUBLISHED)
            )

        return Lesson.objects.all()

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
                IsLessonOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied("You can only add lessons to your own courses.")

        serializer.save()