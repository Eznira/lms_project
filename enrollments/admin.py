from django.contrib import admin

from enrollments.models import Enrollment


# Register your models here.
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "course",
        "enrolled_at",
    )
    list_filter = ("enrolled_at",)
    search_fields = ("student__email", "course__title")