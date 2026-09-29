from django.db.models import Avg, Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .permissions import IsReviewOwnerOrAdmin
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    filterset_fields = [
        "course",
        "rating",
    ]

    search_fields = [
        "comment",
        "student__email",
        "course__title",
    ]

    ordering_fields = [
        "rating",
        "created_at",
        "updated_at",
    ]

    def get_queryset(self):
        return Review.objects.select_related(
            "student",
            "course",
        ).all()

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [IsAuthenticated()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [
                IsAuthenticated(),
                IsReviewOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        url_path="course/(?P<course_id>[^/.]+)/summary",
    )
    def course_summary(self, request, course_id=None):
        summary = Review.objects.filter(
            course_id=course_id,
        ).aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("id"),
        )

        return Response(
            {
                "course": int(course_id),
                "average_rating": round(
                    summary["average_rating"] or 0,
                    2,
                ),
                "total_reviews": summary["total_reviews"],
            },
            status=status.HTTP_200_OK,
        )
