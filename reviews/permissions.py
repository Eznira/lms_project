from rest_framework.permissions import BasePermission


class IsReviewOwnerOrAdmin(BasePermission):
    """
    Students can modify their own reviews.
    Admins can modify any review.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.student == request.user
