from rest_framework import serializers


class StudentCourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    lessons_completed = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    completed = serializers.BooleanField()


class StudentAssignmentScoreSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField()
    assignment_title = serializers.CharField()
    score = serializers.IntegerField()
    total_marks = serializers.IntegerField()
    percentage = serializers.FloatField()


class StudentQuizAttemptSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    quiz_title = serializers.CharField()
    score = serializers.IntegerField()
    total_marks = serializers.IntegerField()
    percentage = serializers.FloatField()
    submitted_at = serializers.DateTimeField()


class StudentQuizPerformanceSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_percentage = serializers.FloatField()
    attempts = StudentQuizAttemptSerializer(many=True)


class StudentAnalyticsSerializer(serializers.Serializer):
    courses_enrolled = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    lessons_completed = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    learning_progress = serializers.FloatField()

    course_progress = StudentCourseProgressSerializer(many=True)

    assignment_scores = StudentAssignmentScoreSerializer(many=True)

    quiz_performance = StudentQuizPerformanceSerializer()

    certificates_earned = serializers.IntegerField()


class InstructorCourseCompletionSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    enrolled_students = serializers.IntegerField()
    completed_students = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class InstructorAssignmentCompletionSerializer(serializers.Serializer):
    total_assignments = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    graded_submissions = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class InstructorQuizPerformanceSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_percentage = serializers.FloatField()


class InstructorAnalyticsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()

    assignment_completion = InstructorAssignmentCompletionSerializer()

    quiz_performance = InstructorQuizPerformanceSerializer()

    average_course_rating = serializers.FloatField()

    course_completion_statistics = InstructorCourseCompletionSerializer(many=True)


class AdminCourseCompletionSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    enrolled_students = serializers.IntegerField()
    completed_students = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class AdminPopularCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    enrollment_count = serializers.IntegerField()


class AdminUsersSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_instructors = serializers.IntegerField()


class AdminCoursesSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    course_completion_rates = AdminCourseCompletionSerializer(many=True)
    most_popular_courses = AdminPopularCourseSerializer(many=True)


class AdminEnrollmentsSerializer(serializers.Serializer):
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    completed_enrollments = serializers.IntegerField()


class AdminStudentEngagementSerializer(serializers.Serializer):
    engaged_students = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    lesson_completions = serializers.IntegerField()
    assignment_submissions = serializers.IntegerField()
    quiz_attempts = serializers.IntegerField()
    exam_attempts = serializers.IntegerField()


class AdminAnalyticsSerializer(serializers.Serializer):
    users = AdminUsersSerializer()
    courses = AdminCoursesSerializer()
    enrollments = AdminEnrollmentsSerializer()
    student_engagement = AdminStudentEngagementSerializer()
    average_course_rating = serializers.FloatField()
