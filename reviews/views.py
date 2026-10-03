from django.db.models import Avg, Count
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .permissions import IsReviewOwnerOrAdmin
from .serializers import ReviewSerializer


@extend_schema_view(
    list=extend_schema(summary="List reviews", description="Retrieve course reviews. Results can be filtered by course or rating and searched by comment, student email, or course title."),
    create=extend_schema(
        summary="Create review",
        description="Create a review for an enrolled course. Each student can review a course only once.",
        examples=[OpenApiExample("Create review", value={"course":1,"rating":5,"comment":"Excellent course."}, request_only=True)],
    ),
    retrieve=extend_schema(summary="Get review", description="Retrieve a single course review by ID."),
    partial_update=extend_schema(
        summary="Update review",
        description="Update a review owned by the authenticated student or an administrator.",
        examples=[OpenApiExample("Update review", value={"rating":4,"comment":"Updated review."}, request_only=True)],
    ),
    destroy=extend_schema(summary="Delete review", description="Delete a review owned by the authenticated student or an administrator."),
)
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

    @extend_schema(
        summary="Get course review summary",
        description="Return the average rating and total number of reviews for a course.",
        responses=OpenApiResponse(description="Object containing course ID, average rating, and total review count."),
    )
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
