from django.contrib import admin

from .models import (
    Assignment,
    AssignmentSubmission,
    ExamAttempt,
    Examination,
    ExamQuestion,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "due_date",
        "created_at",
    )

    list_filter = (
        "course",
        "due_date",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
    )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "student",
        "submitted_at",
        "grade",
    )

    list_filter = (
        "assignment",
        "submitted_at",
        "grade",
    )

    search_fields = (
        "assignment__title",
        "student__email",
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


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
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


@admin.register(ExamQuestion)
class ExaminationQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "examination",
        "question_type",
        "correct_answer",
        "marks",
        "order",
    )

    list_filter = (
        "question_type",
        "examination",
    )

    search_fields = (
        "question_text",
        "examination__title",
        "examination__course__title",
    )

    ordering = (
        "examination",
        "order",
    )


@admin.register(ExamAttempt)
class ExaminationAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "examination",
        "score",
        "total_marks",
        "percentage",
        "started_at",
        "submitted_at",
    )

    list_filter = (
        "examination",
        "submitted_at",
        "started_at",
    )

    search_fields = (
        "student__email",
        "examination__title",
        "examination__course__title",
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


from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_number",
        "student",
        "course",
        "completion_percentage",
        "issued_at",
    )

    list_filter = (
        "course",
        "issued_at",
    )

    search_fields = (
        "certificate_number",
        "student__email",
        "course__title",
    )

    readonly_fields = (
        "certificate_number",
        "completion_percentage",
        "issued_at",
    )

    ordering = ("-issued_at",)
