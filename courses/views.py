from django.db.migrations import serializer
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sqlparse.sql import Assignment

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


@extend_schema_view(
    list=extend_schema(summary="List courses", description="Retrieve courses available to the authenticated user. Students see published courses; instructors see their own courses plus published courses; administrators can view all courses."),
    create=extend_schema(
        summary="Create course",
        description="Create a course and automatically assign it to the authenticated instructor. Administrators can also create courses.",
        examples=[OpenApiExample("Create course", value={"title":"Python Basics","description":"Introduction to Python programming","category":1,"duration":30,"price":"49.99","level":"BEGINNER","status":"DRAFT"}, request_only=True)],
    ),
    retrieve=extend_schema(summary="Get course", description="Retrieve detailed information about a course by ID."),
    update=extend_schema(
        summary="Replace course",
        description="Replace all writable fields of a course. Instructors may update only courses they own; administrators can update any course.",
        examples=[OpenApiExample("Update course", value={"title":"Python Basics Updated","description":"Updated introduction to Python programming","category":1,"duration":40,"price":"59.99","level":"BEGINNER","status":"PUBLISHED"}, request_only=True)],
    ),
    partial_update=extend_schema(
        summary="Update course",
        description="Update selected fields of a course. Instructors may update only courses they own; administrators can update any course.",
        examples=[OpenApiExample("Publish course", value={"status":"PUBLISHED"}, request_only=True)],
    ),
    destroy=extend_schema(summary="Delete course", description="Delete a course. Only the owning instructor or an administrator can perform this operation."),
)
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

        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()
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


@extend_schema_view(
    list=extend_schema(summary="List categories", description="Retrieve all course categories."),
    create=extend_schema(
        summary="Create category",
        description="Create a new course category. Administrators only.",
        examples=[OpenApiExample("Create category", value={"name":"Programming","description":"Courses related to programming and software development"}, request_only=True)],
    ),
    retrieve=extend_schema(summary="Get category", description="Retrieve a category by ID."),
    update=extend_schema(summary="Replace category", description="Replace a category. Administrators only."),
    partial_update=extend_schema(summary="Update category", description="Update selected category fields. Administrators only."),
    destroy=extend_schema(summary="Delete category", description="Delete a category. Administrators only."),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdmin()]

        return [IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(summary="List lessons", description="Retrieve lessons visible to the authenticated user. Students see lessons from published courses they are enrolled in; instructors see lessons for their courses and published courses."),
    create=extend_schema(
        summary="Create lesson",
        description="Create a lesson for a course. Instructors and administrators can create lessons; instructors can assign lessons only to their own courses.",
        examples=[OpenApiExample("Create lesson", value={"course":1,"title":"Introduction to Variables","content":"In this lesson, we cover Python variables and data types.","order":1}, request_only=True)],
    ),
    retrieve=extend_schema(summary="Get lesson", description="Retrieve a lesson by ID."),
    update=extend_schema(summary="Replace lesson", description="Replace all writable fields of a lesson. Only the course owner or an administrator can update it."),
    partial_update=extend_schema(
        summary="Update lesson",
        description="Update selected lesson fields. Only the course owner or an administrator can update it.",
        examples=[OpenApiExample("Update lesson", value={"content":"Partially updated lesson content."}, request_only=True)],
    ),
    destroy=extend_schema(summary="Delete lesson", description="Delete a lesson. Only the course owner or an administrator can delete it."),
)
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "course": ["exact"],
    }

    search_fields = [
        "title",
        "content",
        "course__title",
    ]

    ordering_fields = [
        "title",
        "order",
        "created_at",
        "updated_at",
    ]

    ordering = ["order"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()
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

    @extend_schema(
        summary="Complete lesson",
        description="Mark a lesson as completed for the authenticated student. The student must be enrolled in the lesson's course. Repeating the request returns the existing completion record.",
        request=None,
        responses=LessonCompletionSerializer,
    )
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
