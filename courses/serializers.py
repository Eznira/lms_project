from attr import field, fields
from django.utils.text import slugify
from rest_framework import serializers

from accounts.serializers import StrictFieldsMixin

from .models import Category, Course, Lesson


class CourseSerializer(StrictFieldsMixin, serializers.ModelSerializer):
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
        return (
            f"{obj.instructor.first_name} {obj.instructor.last_name}".strip()
            or obj.instructor.email
        )


class CategorySerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [  # noqa: RUF012
            "id",
            "name",
            "slug",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]  # noqa: RUF012

    def validate(self, attrs):
        name = attrs.get("name")

        if name:
            slug = slugify(name)

            queryset = Category.objects.filter(slug=slug)

            # During PATCH, don't compare the category against itself.
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "name": "A category with this name would generate an existing slug."
                    }
                )

        return attrs

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])

        return super().update(instance, validated_data)


class LessonSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [  # noqa: RUF012
            "id",
            "course",
            "title",
            "content",
            "video",
            "pdf",
            "audio",
            "external_resource",
            "order",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id","created_at", "updated_at"]  # noqa: RUF012
