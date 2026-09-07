from rest_framework import serializers

from .models import Category, Course

    
class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.ReadOnlyField(source="instructor.username")

    class Meta:
        model = Course
        fields = [  # noqa: RUF012
            "id",
            "title",
            "description",
            "category",
            "instructor",
            "duration",
            "price",
            "level",
            "thumbnail",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [  # noqa: RUF012
            "id",
            "instructor",
            "created_at",
            "updated_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [  # noqa: RUF012
            "id",
            "name",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]  # noqa: RUF012
