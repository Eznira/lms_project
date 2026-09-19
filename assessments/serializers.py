from django.utils import timezone
from rest_framework import serializers

from .models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Assignment
        fields = [  # noqa: RUF012
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
