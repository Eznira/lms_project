from django.utils import timezone
from rest_framework import serializers

from .models import Assignment, AssignmentSubmission, QuizAttempt, QuizQuestion, Quiz


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "due_date",
            "total_marks",
            "attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "course_title",
            "created_at",
            "updated_at",
        ]

    def validate_due_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")

        return value

    def validate_total_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total marks must be greater than zero.")

        return value


class AssignmentSubmissionSerializer(serializers.ModelSerializer):

    assignment_title = serializers.CharField(
        source="assignment.title",
        read_only=True,
    )

    student_email = serializers.CharField(
        source="student.email",
        read_only=True,
    )

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "assignment_title",
            "student_email",
            "submission_file",
            "submitted_at",
            "grade",
            "feedback",
        ]
        read_only_fields = [
            "id",
            "assignment_title",
            "student_email",
            "submitted_at",
        ]

    def validate_assignment(self, assignment):
        if assignment.due_date <= timezone.now():
            raise serializers.ValidationError("This assignment is past its due date.")

        return assignment

    def validate_grade(self, value):
        if value < 0:
            raise serializers.ValidationError("Grade cannot be negative.")

        assignment = self.instance.assignment if self.instance else None

        if assignment and value > assignment.total_marks:
            raise serializers.ValidationError(
                f"Grade cannot exceed {assignment.total_marks}."
            )

        return value


class QuizSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    question_count = serializers.IntegerField(
        source="questions.count",
        read_only=True,
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "duration",
            "question_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "course_title",
            "question_count",
            "created_at",
            "updated_at",
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quiz duration must be greater than zero."
            )

        return value


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "quiz",
            "question_text",
            "question_type",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "marks",
            "order",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        question_type = attrs.get(
            "question_type",
            getattr(
                self.instance,
                "question_type",
                None,
            ),
        )

        correct_answer = attrs.get(
            "correct_answer",
            getattr(
                self.instance,
                "correct_answer",
                None,
            ),
        )

        if question_type == "TRUE_FALSE":
            if correct_answer not in ["A", "B"]:
                raise serializers.ValidationError(
                    {"correct_answer": ("True/False questions must use A or B.")}
                )

        if question_type == "MCQ":
            if correct_answer not in ["A", "B", "C", "D"]:
                raise serializers.ValidationError(
                    {"correct_answer": ("MCQ questions must use A, B, C, or D.")}
                )

        return attrs
    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and request.user.role == request.user.Role.STUDENT
        ):
            data.pop("correct_answer", None)

        return data

class QuizAttemptSerializer(serializers.ModelSerializer):

    quiz_title = serializers.CharField(
        source="quiz.title",
        read_only=True,
    )

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "answers",
            "score",
            "total_marks",
            "started_at",
            "submitted_at",
        ]
        read_only_fields = [
            "id",
            "quiz_title",
            "score",
            "total_marks",
            "started_at",
            "submitted_at",
        ]


    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())

    questions = QuizQuestionSerializer(many=True)

    def validate(self, attrs):
        quiz = attrs["quiz"]
        questions = attrs["questions"]

        if not questions:
            raise serializers.ValidationError(
                {"questions": "At least one question is required."}
            )

        orders = [question["order"] for question in questions]

        if len(orders) != len(set(orders)):
            raise serializers.ValidationError(
                {"questions": "Question orders must be unique."}
            )

        existing_orders = set(quiz.questions.values_list("order", flat=True))

        duplicate_orders = existing_orders.intersection(orders)

        if duplicate_orders:
            raise serializers.ValidationError(
                {
                    "questions": (
                        f"These question orders already exist: "
                        f"{sorted(duplicate_orders)}"
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        quiz = validated_data["quiz"]
        questions = validated_data["questions"]

        return [
            QuizQuestion.objects.create(
                quiz=quiz,
                **question,
            )
            for question in questions
        ]