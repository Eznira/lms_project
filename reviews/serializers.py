from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    student_email = serializers.CharField(
        source="student.email",
        read_only=True,
    )

    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "student_email",
            "course",
            "course_title",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_email",
            "course_title",
            "created_at",
            "updated_at",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")

        return value

    def validate_course(self, course):
        user = self.context["request"].user

        if not course.enrollments.filter(student=user).exists():
            raise serializers.ValidationError(
                "You must be enrolled in this course to review it."
            )

        # Prevent duplicate reviews
        existing_review = Review.objects.filter(
            student=user,
            course=course,
        )

        if self.instance:
            existing_review = existing_review.exclude(pk=self.instance.pk)

        if existing_review.exists():
            raise serializers.ValidationError("You have already reviewed this course.")

        return course
