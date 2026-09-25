from django.db.migrations import serializer
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin
from enrollments.models import Enrollment, LessonCompletion
from enrollments.serializers import LessonCompletionSerializer

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

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "category": ["exact"],
        "category__slug": ["exact"],
        "level": ["exact"],
        "status": ["exact"],
    }

    search_fields = [
        "title",
        "description",
        "category__name",
    ]

    ordering_fields = [
        "title",
        "price",
        "duration",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Course.objects.filter(status=Course.Status.PUBLISHED)
        if user.role == user.Role.INSTRUCTOR:
            return Course.objects.filter(
                Q(instructor=user) | Q(status=Course.Status.PUBLISHED)
            )

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
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdmin()]

        return [IsAuthenticated()]


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.STUDENT:
            return Lesson.objects.filter(
                course__status=Course.Status.PUBLISHED,
                course__enrollments__student=user,
            )

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

    def perform_update(self, serializer):
        course = serializer.validated_data.get(
            "course",
            serializer.instance.course,
        )

        if (
            self.request.user.role != self.request.user.Role.ADMIN
            and course.instructor != self.request.user
        ):
            raise PermissionDenied("You can only assign lessons to your own courses.")

        serializer.save()

    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
    )
    def complete(self, request, pk=None):
        lesson = self.get_object()

        if request.user.role != request.user.Role.STUDENT:
            return Response(
                {"detail": "Only students can complete lessons."},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=lesson.course,
        ).exists()

        if not is_enrolled:
            return Response(
                {"detail": "You must be enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        completion, created = LessonCompletion.objects.get_or_create(
            student=request.user,
            lesson=lesson,
        )

        serializer = LessonCompletionSerializer(completion)

        return Response(
            serializer.data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK),
        )
