from django.contrib import admin
from .models import Category, Course


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "instructor",
        "level",
        "status",
        "price",
        "created_at",
    )

    list_filter = (
        "status",
        "level",
        "category",
    )

    search_fields = (
        "title",
        "description",
    )
