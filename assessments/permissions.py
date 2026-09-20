from rest_framework.permissions import BasePermission


class IsAssignmentOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.course.instructor == request.user


class IsSubmissionOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        if request.user.role == request.user.Role.STUDENT:
            return obj.student == request.user

        return obj.assignment.course.instructor == request.user

class IsSubmissionGraderOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return (
            request.user.role == request.user.Role.INSTRUCTOR
            and obj.assignment.course.instructor == request.user
        )