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

class IsQuizOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.course.instructor == request.user


class IsQuizQuestionOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.quiz.course.instructor == request.user


class IsExamOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.course.instructor == request.user


class IsExamQuestionOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.examination.course.instructor == request.user


class IsExamAttemptOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        if request.user.role == request.user.Role.STUDENT:
            return obj.student == request.user

        return obj.examination.course.instructor == request.user

class IsInstructorOrAdminCanGrade(BasePermission):
    """
    Allows instructors to grade attempts for their own courses
    and admins to grade any attempt.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            request.user.Role.INSTRUCTOR,
            request.user.Role.ADMIN,
        ]

    def has_object_permission(self, request, view, obj):
        # Admin can grade any exam attempt
        if request.user.role == request.user.Role.ADMIN:
            return True

        # Instructor can only grade attempts
        # belonging to their own courses
        if request.user.role == request.user.Role.INSTRUCTOR:
            return obj.examination.course.instructor == request.user

        return False

class IsCertificateOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == request.user.Role.ADMIN:
            return True

        return obj.student == request.user