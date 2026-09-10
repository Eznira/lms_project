from rest_framework.permissions import BasePermission

class IsVerified(BasePermission):
    message = "Email verification is required to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.email_verified


class IsAdmin(BasePermission):
    message = "Only admins can perform this action."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsInstructor(BasePermission):
    message = "Only instructors can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.INSTRUCTOR
        )


class IsStudent(BasePermission):
    message = "Only students can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.STUDENT
        )
