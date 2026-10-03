from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.services import NotificationService

from .models import Enrollment
from .serializers import EnrollmentSerializer


@extend_schema_view(
    list=extend_schema(summary="List enrollments", description="List enrollments visible to the authenticated user. Students see their own enrollments; administrators can view all enrollments."),
    create=extend_schema(
        summary="Enroll in course",
        description="Enroll the authenticated student in a course. Duplicate enrollments are rejected.",
        examples=[OpenApiExample("Enroll in course", value={"course":1}, request_only=True)],
    ),
    retrieve=extend_schema(summary="Get enrollment", description="Retrieve an enrollment by ID."),
    destroy=extend_schema(summary="Delete enrollment", description="Remove an enrollment. Students can manage their own enrollment records."),
)
class EnrollmentViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "delete", "head", "options"]
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()

        user = self.request.user

        if user.role == user.Role.ADMIN:
            return Enrollment.objects.all()

        return Enrollment.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        if request.user.role != request.user.Role.STUDENT:
            return Response(
                {"detail": "Only students can enroll in courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = request.data.get("course")

        if Enrollment.objects.filter(
            student=request.user,
            course=course,
        ).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save(student=request.user)

        headers = self.get_success_headers(serializer.data)

        NotificationService.enrollment_notification(
            student=request.user,
            course=enrollment.course,
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
