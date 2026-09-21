from django.contrib import admin

from .models import (
    Quiz,
    QuizQuestion,
    QuizAttempt,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "duration",
        "question_count",
        "created_at",
    )

    list_filter = (
        "course",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
    )

    ordering = (
        "course",
        "title",
    )

    @admin.display(description="Questions")
    def question_count(self, obj):
        return obj.questions.count()


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "quiz",
        "question_type",
        "correct_answer",
        "marks",
        "order",
    )

    list_filter = (
        "question_type",
        "quiz",
    )

    search_fields = (
        "question_text",
        "quiz__title",
        "quiz__course__title",
    )

    ordering = (
        "quiz",
        "order",
    )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "quiz",
        "score",
        "total_marks",
        "percentage",
        "started_at",
        "submitted_at",
    )

    list_filter = (
        "quiz",
        "submitted_at",
        "started_at",
    )

    search_fields = (
        "student__email",
        "quiz__title",
        "quiz__course__title",
    )

    ordering = ("-started_at",)

    @admin.display(description="Percentage")
    def percentage(self, obj):
        if obj.total_marks == 0:
            return 0

        return round(
            (obj.score / obj.total_marks) * 100,
            2,
        )
