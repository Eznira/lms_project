from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import Category, Course
from .permissions import (
    IsCourseOwnerOrAdmin,
    IsInstructorOrAdmin,
)
from .serializers import CategorySerializer, CourseSerializer


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