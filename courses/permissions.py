from rest_framework.permissions import BasePermission


class IsInstructorOrAdmin(BasePermission):
    """
    Allows instructors and admins to create courses.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            request.user.Role.INSTRUCTOR,
            request.user.Role.ADMIN,
        ]


class IsCourseOwnerOrAdmin(BasePermission):
    """
    Allows the course instructor or an admin to modify a course.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.instructor == request.user

class IsLessonOwnerOrAdmin(BasePermission):
    """
    Allows the lesson's course instructor or an admin to modify a lesson.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.course.instructor == request.user