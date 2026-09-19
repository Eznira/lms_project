from rest_framework.permissions import BasePermission


class IsAssignmentOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.course.instructor == request.user
