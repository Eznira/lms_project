from django.contrib import admin

from .models import Category, Course, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "instructor",
        "level",
        "price",
        "status",
        "created_at",
    ]
    list_filter = ["status", "level", "category"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "course",
        "order",
        "created_at",
        "updated_at",
    ]
    list_filter = ["course"]
    search_fields = [
        "title",
        "content",
        "course__title",
    ]
    ordering = ["course", "order"]