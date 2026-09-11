from os import name

from rest_framework import serializers

from .models import Category, Course

class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    instructor = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [  # noqa: RUF012
            "id",
            "title",
            "description",
            "category",
            "category_name",
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
            "category_name",
            "instructor",
            "created_at",
            "updated_at",
        ]

    def get_instructor(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip()

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
