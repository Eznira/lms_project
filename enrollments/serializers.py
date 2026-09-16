from rest_framework import serializers

from .models import Enrollment, LessonCompletion


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(
        source="lesson.title",
        read_only=True,
    )

    class Meta:
        model = LessonCompletion
        fields = [  # noqa: RUF012
            "id",
            "lesson",
            "lesson_title",
            "completed_at",
        ]
        read_only_fields = [  # noqa: RUF012
            "id",
            "lesson_title",
            "completed_at",
        ]






class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Enrollment
        fields = [  # noqa: RUF012
            "id",
            "course",
            "course_title",
            "enrolled_at",
        ]
        read_only_fields = [  # noqa: RUF012
            "id",
            "course_title",
            "enrolled_at",
        ]
        
    def validate_course(self, course):
        if course.status != course.Status.PUBLISHED:
            raise serializers.ValidationError(
                "You can only enroll in published courses."
            )

        return course