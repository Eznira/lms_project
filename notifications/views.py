from django.shortcuts import render

# Create your views here.
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List my notifications",
        description="Return notifications belonging to the authenticated user.",
    ),
    retrieve=extend_schema(
        summary="Get my notification",
        description="Return a single notification belonging to the authenticated user.",
    ),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "notification_type",
        "is_read",
    ]

    search_fields = [
        "title",
        "message",
    ]

    ordering_fields = [
        "created_at",
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            return Notification.objects.all()

        return Notification.objects.filter(
            recipient=user,
        )

    @extend_schema(
        summary="Mark notification as read",
        description="Mark one of the authenticated user's notifications as read.",
        request=None,
        responses=NotificationSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read",
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Mark all notifications as read",
        description="Mark all notifications belonging to the authenticated user as read.",
        request=None,
        responses={"200": None},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="mark-all-read",
    )
    def mark_all_read(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

        return Response(
            {
                "detail": "All notifications marked as read.",
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Get unread notification count",
        description="Return the number of unread notifications for the authenticated user.",
        request=None,
        responses={"200": None},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
    )
    def unread_count(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

        return Response(
            {
                "unread_count": count,
            },
            status=status.HTTP_200_OK,
        )
