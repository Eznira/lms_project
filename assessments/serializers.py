from django.utils import timezone
from rest_framework import serializers

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "due_date",
            "total_marks",
            "attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "course_title",
            "created_at",
            "updated_at",
        ]

    def validate_due_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")

        return value

    def validate_total_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total marks must be greater than zero.")

        return value


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(
        source="assignment.title",
        read_only=True,
    )

    student_email = serializers.CharField(
        source="student.email",
        read_only=True,
    )

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "assignment_title",
            "student_email",
            "submission_file",
            "submitted_at",
            "grade",
            "feedback",
        ]
        read_only_fields = [
            "id",
            "assignment_title",
            "student_email",
            "submitted_at",
        ]

    def validate_assignment(self, assignment):
        if assignment.due_date <= timezone.now():
            raise serializers.ValidationError("This assignment is past its due date.")

        return assignment

    def validate_grade(self, value):
        if value < 0:
            raise serializers.ValidationError("Grade cannot be negative.")

        assignment = self.instance.assignment if self.instance else None

        if assignment and value > assignment.total_marks:
            raise serializers.ValidationError(
                f"Grade cannot exceed {assignment.total_marks}."
            )

        return value