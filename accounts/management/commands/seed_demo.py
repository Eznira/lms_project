from datetime import timedelta
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import InstructorProfile, StudentProfile, User
from assessments.models import (
    Assignment,
    AssignmentSubmission,
    Certificate,
    ExamAttempt,
    ExamQuestion,
    Examination,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)
from courses.models import Category, Course, Lesson
from enrollments.models import Enrollment, LessonCompletion
from notifications.models import Notification
from reviews.models import Review


class Command(BaseCommand):
    help = "Create realistic demo data for the LMS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before seeding.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting LMS demo seed..."))

        if options["reset"]:
            self.reset_demo_data()

        self.create_users()
        self.create_categories()
        self.create_courses()
        self.create_lessons()
        self.create_enrollments()
        self.create_lesson_completions()
        self.create_assignments()
        self.create_assignment_submissions()
        self.create_quizzes()
        self.create_quiz_questions()
        self.create_quiz_attempts()
        self.create_examinations()
        self.create_exam_questions()
        self.create_exam_attempts()
        self.create_certificates()
        self.create_reviews()
        self.create_notifications()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo data created successfully!"))

        self.print_credentials()

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    def create_users(self):
        self.admin, _ = User.objects.get_or_create(
            email="admin@lmsdemo.com",
            defaults={
                "first_name": "System",
                "last_name": "Administrator",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "email_verified": True,
            },
        )

        self.admin.set_password("DemoAdmin123!")
        self.admin.role = User.Role.ADMIN
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.is_active = True
        self.admin.email_verified = True
        self.admin.save()

        instructor_data = [
            (
                "john.instructor@lmsdemo.com",
                "John",
                "Okafor",
                "B.Sc. Computer Science",
                "Backend Development",
            ),
            (
                "sarah.instructor@lmsdemo.com",
                "Sarah",
                "Eze",
                "B.Sc. Software Engineering",
                "Mobile Development",
            ),
        ]

        self.instructors = []

        for (
            email,
            first_name,
            last_name,
            qualification,
            specialization,
        ) in instructor_data:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": User.Role.INSTRUCTOR,
                    "is_active": True,
                    "email_verified": True,
                },
            )

            user.first_name = first_name
            user.last_name = last_name
            user.role = User.Role.INSTRUCTOR
            user.is_active = True
            user.email_verified = True
            user.set_password("DemoInstructor123!")
            user.save()

            InstructorProfile.objects.update_or_create(
                user=user,
                defaults={
                    "qualification": qualification,
                    "specialization": specialization,
                    "biography": (
                        f"{first_name} is an experienced "
                        f"{specialization.lower()} instructor."
                    ),
                    "phone": "08000000001",
                },
            )

            self.instructors.append(user)

        student_data = [
            ("student1@lmsdemo.com", "David", "Okoro"),
            ("student2@lmsdemo.com", "Grace", "Adeyemi"),
            ("student3@lmsdemo.com", "Michael", "Eze"),
            ("student4@lmsdemo.com", "Daniel", "Ibrahim"),
            ("student5@lmsdemo.com", "Esther", "Nwosu"),
        ]

        self.students = []

        for index, (email, first_name, last_name) in enumerate(
            student_data,
            start=1,
        ):
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": User.Role.STUDENT,
                    "is_active": True,
                    "email_verified": True,
                },
            )

            user.first_name = first_name
            user.last_name = last_name
            user.role = User.Role.STUDENT
            user.is_active = True
            user.email_verified = True
            user.set_password("DemoStudent123!")
            user.save()

            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    "phone": f"0800000000{index}",
                    "biography": f"{first_name} is a demo LMS student.",
                },
            )

            self.students.append(user)

        self.stdout.write("  Users created.")

    # ---------------------------------------------------------
    # CATEGORIES
    # ---------------------------------------------------------

    def create_categories(self):
        category_data = [
            (
                "Programming",
                "programming",
                "Programming fundamentals and software development.",
            ),
            (
                "Web Development",
                "web-development",
                "Backend and web API development.",
            ),
            (
                "Mobile Development",
                "mobile-development",
                "Mobile application development.",
            ),
            (
                "Database",
                "database",
                "Database design, SQL and data management.",
            ),
        ]

        self.categories = {}

        for name, slug, description in category_data:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                },
            )
            self.categories[slug] = category

        self.stdout.write("  Categories created.")

    # ---------------------------------------------------------
    # COURSES
    # ---------------------------------------------------------

    def create_courses(self):
        course_data = [
            {
                "key": "python",
                "title": "Python Fundamentals",
                "description": ("Learn Python programming from the ground up."),
                "category": self.categories["programming"],
                "instructor": self.instructors[0],
                "duration": 3,
                "price": Decimal("0.00"),
                "level": Course.Level.BEGINNER,
                "status": Course.Status.PUBLISHED,
            },
            {
                "key": "django",
                "title": "Django REST API Development",
                "description": (
                    "Build professional REST APIs with Django REST Framework."
                ),
                "category": self.categories["web-development"],
                "instructor": self.instructors[0],
                "duration": 4,
                "price": Decimal("25000.00"),
                "level": Course.Level.INTERMEDIATE,
                "status": Course.Status.PUBLISHED,
            },
            {
                "key": "flutter",
                "title": "Flutter Mobile Development",
                "description": (
                    "Build cross-platform mobile applications with Flutter and Dart."
                ),
                "category": self.categories["mobile-development"],
                "instructor": self.instructors[1],
                "duration": 4,
                "price": Decimal("30000.00"),
                "level": Course.Level.INTERMEDIATE,
                "status": Course.Status.PUBLISHED,
            },
            {
                "key": "database",
                "title": "Database Fundamentals",
                "description": ("Learn relational databases, SQL and database design."),
                "category": self.categories["database"],
                "instructor": self.instructors[1],
                "duration": 2,
                "price": Decimal("15000.00"),
                "level": Course.Level.BEGINNER,
                "status": Course.Status.DRAFT,
            },
        ]

        self.courses = {}

        for data in course_data:
            course, _ = Course.objects.update_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "category": data["category"],
                    "instructor": data["instructor"],
                    "duration": data["duration"],
                    "price": data["price"],
                    "level": data["level"],
                    "status": data["status"],
                },
            )

            self.courses[data["key"]] = course

        self.stdout.write("  Courses created.")

    # ---------------------------------------------------------
    # LESSONS
    # ---------------------------------------------------------

    def create_lessons(self):
        lesson_data = {
            "python": [
                "Introduction to Python",
                "Variables and Data Types",
                "Control Flow",
                "Functions",
                "Object-Oriented Programming",
            ],
            "django": [
                "Introduction to Django",
                "Django Models",
                "Serializers",
                "API Views and ViewSets",
                "JWT Authentication",
            ],
            "flutter": [
                "Flutter Fundamentals",
                "Widgets",
                "Layouts",
                "State Management",
                "API Integration",
            ],
            "database": [
                "Introduction to Databases",
                "Relational Databases",
                "SQL Fundamentals",
                "Relationships",
                "Database Design",
            ],
        }

        self.lessons = {}

        for course_key, titles in lesson_data.items():
            course = self.courses[course_key]
            self.lessons[course_key] = []

            for order, title in enumerate(titles, start=1):
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    order=order,
                    defaults={
                        "title": title,
                        "content": (
                            f"This is demo content for {title}. "
                            f"It belongs to the {course.title} course."
                        ),
                    },
                )

                self.lessons[course_key].append(lesson)

        self.stdout.write("  Lessons created.")

    # ---------------------------------------------------------
    # ENROLLMENTS
    # ---------------------------------------------------------

    def create_enrollments(self):
        enrollment_map = {
            0: ["python", "django"],
            1: ["django"],
            2: ["python"],
            3: ["python", "flutter"],
            4: ["django", "flutter"],
        }

        for student_index, course_keys in enrollment_map.items():
            student = self.students[student_index]

            for course_key in course_keys:
                Enrollment.objects.get_or_create(
                    student=student,
                    course=self.courses[course_key],
                )

        self.stdout.write("  Enrollments created.")

    # ---------------------------------------------------------
    # LESSON COMPLETIONS
    # ---------------------------------------------------------

    def create_lesson_completions(self):
        completion_map = {
            0: {
                "python": 5,
            },
            1: {
                "django": 3,
            },
            3: {
                "python": 2,
                "flutter": 4,
            },
            4: {
                "django": 3,
            },
        }

        for student_index, courses in completion_map.items():
            student = self.students[student_index]

            for course_key, count in courses.items():
                for lesson in self.lessons[course_key][:count]:
                    LessonCompletion.objects.get_or_create(
                        student=student,
                        lesson=lesson,
                    )

        self.stdout.write("  Lesson progress created.")

    # ---------------------------------------------------------
    # ASSIGNMENTS
    # ---------------------------------------------------------

    def create_assignments(self):
        self.assignments = {}

        assignment_data = [
            (
                "python",
                "Build a Calculator",
                "Create a command-line calculator using Python.",
                20,
            ),
            (
                "django",
                "Build a REST API",
                "Create a REST API with Django REST Framework.",
                30,
            ),
            (
                "flutter",
                "Build a Course List App",
                "Build a Flutter application that displays a list of courses.",
                25,
            ),
        ]

        for course_key, title, description, total_marks in assignment_data:
            assignment, _ = Assignment.objects.update_or_create(
                course=self.courses[course_key],
                title=title,
                defaults={
                    "description": description,
                    "due_date": timezone.now() + timedelta(days=30),
                    "total_marks": total_marks,
                },
            )

            self.assignments[course_key] = assignment

        self.stdout.write("  Assignments created.")

    # ---------------------------------------------------------
    # ASSIGNMENT SUBMISSIONS
    # ---------------------------------------------------------

    def create_assignment_submissions(self):
        submissions = [
            ("python", 0, 18, "Excellent implementation."),
            ("django", 0, 27, "Very good REST API implementation."),
            ("django", 1, 22, "Good work. Improve validation."),
            ("python", 3, 15, "Good start."),
            ("flutter", 4, 20, "Nice Flutter implementation."),
        ]

        for course_key, student_index, grade, feedback in submissions:
            assignment = self.assignments[course_key]
            student = self.students[student_index]

            submission, _ = AssignmentSubmission.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={
                    "submission_file": ContentFile(
                        f"Demo submission by {student.email}",
                        name=f"demo_submission_{student_index + 1}.txt",
                    ),
                },
            )

            if submission.grade is None:
                submission.grade = grade
                submission.feedback = feedback
                submission.save(update_fields=["grade", "feedback"])

        self.stdout.write("  Assignment submissions created.")

    # ---------------------------------------------------------
    # QUIZZES
    # ---------------------------------------------------------

    def create_quizzes(self):
        self.quizzes = {}

        quiz_data = [
            (
                "python",
                "Python Fundamentals Quiz",
                "Test your understanding of Python fundamentals.",
            ),
            (
                "django",
                "Django REST API Quiz",
                "Test your understanding of Django REST Framework.",
            ),
            (
                "flutter",
                "Flutter Fundamentals Quiz",
                "Test your understanding of Flutter development.",
            ),
        ]

        for course_key, title, description in quiz_data:
            quiz, _ = Quiz.objects.update_or_create(
                course=self.courses[course_key],
                title=title,
                defaults={
                    "description": description,
                    "duration": 30,
                },
            )

            self.quizzes[course_key] = quiz

        self.stdout.write("  Quizzes created.")

    # ---------------------------------------------------------
    # QUIZ QUESTIONS
    # ---------------------------------------------------------

    def create_quiz_questions(self):
        questions = {
            "python": [
                (
                    "Which keyword defines a function in Python?",
                    "A",
                    "func",
                    "def",
                    "function",
                    "define",
                ),
                (
                    "Which data type stores key-value pairs?",
                    "B",
                    "List",
                    "Dictionary",
                    "Tuple",
                    "Set",
                ),
                (
                    "Which symbol starts a comment in Python?",
                    "C",
                    "//",
                    "/*",
                    "#",
                    "--",
                ),
                (
                    "Python is case-sensitive.",
                    "A",
                    "True",
                    "False",
                    "",
                    "",
                ),
                (
                    "Which keyword creates a class?",
                    "D",
                    "object",
                    "struct",
                    "type",
                    "class",
                ),
            ],
            "django": [
                (
                    "What does DRF stand for?",
                    "A",
                    "Django REST Framework",
                    "Django Routing Framework",
                    "Data REST Format",
                    "Django Response Framework",
                ),
                (
                    "Which class is commonly used for model-based APIs?",
                    "B",
                    "APIView",
                    "ModelViewSet",
                    "HttpView",
                    "RESTModel",
                ),
                (
                    "JWT is commonly used for authentication.",
                    "A",
                    "True",
                    "False",
                    "",
                    "",
                ),
                (
                    "Which HTTP method normally creates a resource?",
                    "C",
                    "GET",
                    "PATCH",
                    "POST",
                    "DELETE",
                ),
                (
                    "Which package provides JWT authentication in this project?",
                    "D",
                    "django-auth",
                    "jwt-django",
                    "rest-jwt",
                    "djangorestframework-simplejwt",
                ),
            ],
            "flutter": [
                (
                    "Which language is used by Flutter?",
                    "A",
                    "Dart",
                    "Java",
                    "Kotlin",
                    "Swift",
                ),
                (
                    "Everything in Flutter's UI is built around what?",
                    "B",
                    "Controllers",
                    "Widgets",
                    "Activities",
                    "Fragments",
                ),
                (
                    "Flutter supports hot reload.",
                    "A",
                    "True",
                    "False",
                    "",
                    "",
                ),
                (
                    "Which widget is commonly used for vertical layouts?",
                    "C",
                    "Row",
                    "Stack",
                    "Column",
                    "Wrap",
                ),
                (
                    "Which file normally contains Flutter dependencies?",
                    "D",
                    "config.json",
                    "flutter.json",
                    "dependencies.yaml",
                    "pubspec.yaml",
                ),
            ],
        }

        self.quiz_questions = {}

        for course_key, question_list in questions.items():
            quiz = self.quizzes[course_key]
            self.quiz_questions[course_key] = []

            for order, data in enumerate(question_list, start=1):
                (
                    question_text,
                    correct_answer,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                ) = data

                question_type = (
                    QuizQuestion.QuestionType.TRUE_FALSE
                    if option_c == ""
                    else QuizQuestion.QuestionType.MCQ
                )

                question, _ = QuizQuestion.objects.update_or_create(
                    quiz=quiz,
                    order=order,
                    defaults={
                        "question_text": question_text,
                        "question_type": question_type,
                        "option_a": option_a,
                        "option_b": option_b,
                        "option_c": option_c,
                        "option_d": option_d,
                        "correct_answer": correct_answer,
                        "marks": 1,
                    },
                )

                self.quiz_questions[course_key].append(question)

        self.stdout.write("  Quiz questions created.")

    # ---------------------------------------------------------
    # QUIZ ATTEMPTS
    # ---------------------------------------------------------

    def create_quiz_attempts(self):
        attempts = [
            ("python", 0, 5),
            ("django", 1, 4),
            ("flutter", 3, 3),
            ("django", 4, 5),
        ]

        for course_key, student_index, score in attempts:
            quiz = self.quizzes[course_key]
            student = self.students[student_index]
            questions = self.quiz_questions[course_key]

            answers = {}

            for question in questions:
                if len(answers) < score:
                    answers[str(question.id)] = question.correct_answer
                else:
                    wrong_answer = "A" if question.correct_answer != "A" else "B"
                    answers[str(question.id)] = wrong_answer

            attempt, _ = QuizAttempt.objects.get_or_create(
                quiz=quiz,
                student=student,
                defaults={
                    "answers": answers,
                    "score": score,
                    "total_marks": sum(q.marks for q in questions),
                    "submitted_at": timezone.now(),
                },
            )

            if attempt.submitted_at is None:
                attempt.answers = answers
                attempt.score = score
                attempt.total_marks = sum(q.marks for q in questions)
                attempt.submitted_at = timezone.now()
                attempt.save()

        self.stdout.write("  Quiz attempts created.")

    # ---------------------------------------------------------
    # EXAMINATIONS
    # ---------------------------------------------------------

    def create_examinations(self):
        now = timezone.now()

        self.examinations = {}

        python_exam, _ = Examination.objects.update_or_create(
            course=self.courses["python"],
            title="Python Final Examination",
            defaults={
                "description": ("Final examination for Python Fundamentals."),
                "duration": 60,
                "start_time": now - timedelta(days=7),
                "end_time": now - timedelta(days=6),
                "status": Examination.Status.COMPLETED,
            },
        )

        django_exam, _ = Examination.objects.update_or_create(
            course=self.courses["django"],
            title="Django REST API Final Examination",
            defaults={
                "description": ("Active examination for Django REST API Development."),
                "duration": 60,
                "start_time": now - timedelta(minutes=30),
                "end_time": now + timedelta(minutes=90),
                "status": Examination.Status.ONGOING,
            },
        )

        self.examinations["python"] = python_exam
        self.examinations["django"] = django_exam

        self.stdout.write("  Examinations created.")

    # ---------------------------------------------------------
    # EXAM QUESTIONS
    # ---------------------------------------------------------

    def create_exam_questions(self):
        questions = {
            "python": [
                (
                    "Which keyword defines a function?",
                    ExamQuestion.QuestionType.MCQ,
                    "A",
                    "def",
                    "class",
                    "func",
                    "define",
                    5,
                ),
                (
                    "Python supports object-oriented programming.",
                    ExamQuestion.QuestionType.TRUE_FALSE,
                    "A",
                    "True",
                    "False",
                    "",
                    "",
                    5,
                ),
                (
                    "Explain the difference between a list and a tuple.",
                    ExamQuestion.QuestionType.ESSAY,
                    "",
                    "",
                    "",
                    "",
                    "",
                    5,
                ),
                (
                    "What data structure stores key-value pairs?",
                    ExamQuestion.QuestionType.MCQ,
                    "B",
                    "List",
                    "Dictionary",
                    "Tuple",
                    "Set",
                    5,
                ),
            ],
            "django": [
                (
                    "What does DRF stand for?",
                    ExamQuestion.QuestionType.MCQ,
                    "A",
                    "Django REST Framework",
                    "Django Routing Framework",
                    "Data REST Format",
                    "Django Response Framework",
                    5,
                ),
                (
                    "JWT can be used for API authentication.",
                    ExamQuestion.QuestionType.TRUE_FALSE,
                    "A",
                    "True",
                    "False",
                    "",
                    "",
                    5,
                ),
                (
                    "Explain the purpose of serializers in DRF.",
                    ExamQuestion.QuestionType.ESSAY,
                    "",
                    "",
                    "",
                    "",
                    "",
                    5,
                ),
                (
                    "Which HTTP method is normally used to create a resource?",
                    ExamQuestion.QuestionType.MCQ,
                    "C",
                    "GET",
                    "PATCH",
                    "POST",
                    "DELETE",
                    5,
                ),
            ],
        }

        self.exam_questions = {}

        for exam_key, question_list in questions.items():
            examination = self.examinations[exam_key]
            self.exam_questions[exam_key] = []

            for order, data in enumerate(question_list, start=1):
                (
                    question_text,
                    question_type,
                    correct_answer,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                    marks,
                ) = data

                question, _ = ExamQuestion.objects.update_or_create(
                    examination=examination,
                    order=order,
                    defaults={
                        "question_text": question_text,
                        "question_type": question_type,
                        "correct_answer": correct_answer,
                        "option_a": option_a,
                        "option_b": option_b,
                        "option_c": option_c,
                        "option_d": option_d,
                        "marks": marks,
                    },
                )

                self.exam_questions[exam_key].append(question)

        self.stdout.write("  Exam questions created.")

    # ---------------------------------------------------------
    # EXAM ATTEMPTS
    # ---------------------------------------------------------

    def create_exam_attempts(self):
        # Python completed exam
        python_exam = self.examinations["python"]
        python_questions = self.exam_questions["python"]
        student = self.students[0]

        python_answers = {
            str(python_questions[0].id): "A",
            str(python_questions[1].id): "A",
            str(python_questions[2].id): (
                "A list is mutable while a tuple is immutable."
            ),
            str(python_questions[3].id): "B",
        }

        python_attempt, _ = ExamAttempt.objects.get_or_create(
            examination=python_exam,
            student=student,
            defaults={
                "answers": python_answers,
                "score": 17,
                "total_marks": 20,
                "submitted_at": timezone.now() - timedelta(days=6),
            },
        )

        if python_attempt.submitted_at is None:
            python_attempt.answers = python_answers
            python_attempt.score = 17
            python_attempt.total_marks = 20
            python_attempt.submitted_at = timezone.now() - timedelta(days=6)
            python_attempt.save()

        # Django active exam attempt
        django_exam = self.examinations["django"]
        django_questions = self.exam_questions["django"]
        student = self.students[4]

        django_attempt, _ = ExamAttempt.objects.get_or_create(
            examination=django_exam,
            student=student,
            defaults={
                "answers": {},
                "score": 0,
                "total_marks": 20,
                "submitted_at": None,
            },
        )

        # Keep this attempt unsubmitted so you can demonstrate
        # Start -> Submit -> Grade manually through Swagger.
        django_attempt.answers = {}
        django_attempt.score = 0
        django_attempt.total_marks = 20
        django_attempt.submitted_at = None
        django_attempt.manual_grades = {}
        django_attempt.save()

        self.stdout.write("  Exam attempts created.")

    # ---------------------------------------------------------
    # CERTIFICATES
    # ---------------------------------------------------------

    def create_certificates(self):
        student = User.objects.get(email="student1@lmsdemo.com")
        course = Course.objects.get(title="Python Fundamentals")

        assignment = Assignment.objects.get(
            title="Build a Calculator",
            course=course,
        )

        assignment_submission = AssignmentSubmission.objects.get(
            assignment=assignment,
            student=student,
        )

        quiz = Quiz.objects.get(
            title="Python Fundamentals Quiz",
            course=course,
        )

        quiz_attempt = (
            QuizAttempt.objects.filter(
                quiz=quiz,
                student=student,
                submitted_at__isnull=False,
            )
            .order_by("-score")
            .first()
        )

        examination = Examination.objects.get(
            title="Python Final Examination",
            course=course,
        )

        exam_attempt = (
            ExamAttempt.objects.filter(
                examination=examination,
                student=student,
                submitted_at__isnull=False,
            )
            .order_by("-score")
            .first()
        )

        percentages = []

        # Assignment percentage
        if assignment_submission.grade is not None and assignment.total_marks > 0:
            assignment_percentage = (
                assignment_submission.grade / assignment.total_marks
            ) * 100

            percentages.append(assignment_percentage)

        # Quiz percentage
        if quiz_attempt and quiz_attempt.total_marks > 0:
            quiz_percentage = (quiz_attempt.score / quiz_attempt.total_marks) * 100

            percentages.append(quiz_percentage)

        # Examination percentage
        if exam_attempt and exam_attempt.total_marks > 0:
            exam_percentage = (exam_attempt.score / exam_attempt.total_marks) * 100

            percentages.append(exam_percentage)

        completion_percentage = (
            sum(percentages) / len(percentages) if percentages else 0
        )

        certificate, created = Certificate.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                "completion_percentage": round(
                    Decimal(str(completion_percentage)),
                    2,
                ),
            },
        )

        if not created:
            certificate.completion_percentage = round(
                Decimal(str(completion_percentage)),
                2,
            )
            certificate.save(update_fields=["completion_percentage"])

        self.stdout.write("  Certificates created.")

    def calculate_demo_completion_percentage(self, student, course):
        assignment = Assignment.objects.filter(
            course=course,
            submissions__student=student,
            submissions__grade__isnull=False,
        ).first()

        assignment_percentage = Decimal("0")

        if assignment:
            submission = assignment.submissions.filter(
                student=student,
                grade__isnull=False,
            ).first()

            if submission and assignment.total_marks:
                assignment_percentage = (
                    Decimal(submission.grade) / Decimal(assignment.total_marks)
                ) * 100

        quiz = self.quizzes["python"]

        quiz_attempt = (
            QuizAttempt.objects.filter(
                quiz=quiz,
                student=student,
                submitted_at__isnull=False,
            )
            .order_by("-score")
            .first()
        )

        quiz_percentage = Decimal("0")

        if quiz_attempt and quiz_attempt.total_marks:
            quiz_percentage = (
                Decimal(quiz_attempt.score) / Decimal(quiz_attempt.total_marks)
            ) * 100

        exam = self.examinations["python"]

        exam_attempt = (
            ExamAttempt.objects.filter(
                examination=exam,
                student=student,
                submitted_at__isnull=False,
            )
            .order_by("-score")
            .first()
        )

        exam_percentage = Decimal("0")

        if exam_attempt and exam_attempt.total_marks:
            exam_percentage = (
                Decimal(exam_attempt.score) / Decimal(exam_attempt.total_marks)
            ) * 100

        percentages = [
            assignment_percentage,
            quiz_percentage,
            exam_percentage,
        ]

        return sum(percentages) / Decimal(len(percentages))

    # ---------------------------------------------------------
    # REVIEWS
    # ---------------------------------------------------------

    def create_reviews(self):
        reviews = [
            (0, "python", 5, "Excellent Python course."),
            (0, "django", 4, "Very practical and well structured."),
            (1, "django", 4, "Great introduction to APIs."),
            (3, "flutter", 5, "The Flutter lessons are very helpful."),
            (4, "flutter", 4, "Good course with practical examples."),
        ]

        for student_index, course_key, rating, comment in reviews:
            Review.objects.update_or_create(
                student=self.students[student_index],
                course=self.courses[course_key],
                defaults={
                    "rating": rating,
                    "comment": comment,
                },
            )

        self.stdout.write("  Reviews created.")

    # ---------------------------------------------------------
    # NOTIFICATIONS
    # ---------------------------------------------------------

    def create_notifications(self):
        notification_data = [
            (
                self.students[0],
                Notification.NotificationType.GRADE,
                "Assignment Graded",
                "Your Python assignment has been graded.",
            ),
            (
                self.students[0],
                Notification.NotificationType.GRADE,
                "Exam Result Available",
                "Your Python final examination result is available.",
            ),
            (
                self.students[0],
                Notification.NotificationType.CERTIFICATE,
                "Certificate Issued",
                "Your Python Fundamentals certificate has been issued.",
            ),
            (
                self.students[1],
                Notification.NotificationType.ENROLLMENT,
                "Enrollment Successful",
                "You have been enrolled in Django REST API Development.",
            ),
            (
                self.students[1],
                Notification.NotificationType.GRADE,
                "Assignment Graded",
                "Your Django assignment has been graded.",
            ),
            (
                self.instructors[0],
                Notification.NotificationType.ASSIGNMENT_SUBMISSION,
                "New Assignment Submission",
                "A student submitted a Django assignment.",
            ),
            (
                self.instructors[0],
                Notification.NotificationType.EXAM_SUBMISSION,
                "Exam Submission",
                "A student submitted an examination attempt.",
            ),
            (
                self.admin,
                Notification.NotificationType.GENERAL,
                "Demo LMS",
                "Demo LMS data has been seeded successfully.",
            ),
        ]

        for recipient, notification_type, title, message in notification_data:
            Notification.objects.get_or_create(
                recipient=recipient,
                title=title,
                defaults={
                    "notification_type": notification_type,
                    "message": message,
                },
            )

        self.stdout.write("  Notifications created.")

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset_demo_data(self):
        self.stdout.write("Resetting demo data...")

        demo_emails = [
            "admin@lmsdemo.com",
            "john.instructor@lmsdemo.com",
            "sarah.instructor@lmsdemo.com",
            "student1@lmsdemo.com",
            "student2@lmsdemo.com",
            "student3@lmsdemo.com",
            "student4@lmsdemo.com",
            "student5@lmsdemo.com",
        ]

        demo_category_slugs = [
            "programming",
            "web-development",
            "mobile-development",
            "database",
        ]

        # Get demo courses before deleting anything.
        demo_courses = Course.objects.filter(
            title__in=[
                "Python Fundamentals",
                "Django REST API Development",
                "Flutter Mobile Development",
                "Database Fundamentals",
            ]
        )

        # Delete demo courses first.
        #
        # Course has PROTECT on instructor, so instructors cannot
        # be deleted until these courses are removed.
        demo_courses.delete()

        # Delete demo categories.
        Category.objects.filter(slug__in=demo_category_slugs).delete()

        # Now the demo instructors can safely be deleted.
        User.objects.filter(email__in=demo_emails).delete()

        self.stdout.write(self.style.WARNING("  Existing demo records removed."))

    # ---------------------------------------------------------
    # CREDENTIALS
    # ---------------------------------------------------------

    def print_credentials(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("DEMO LOGIN CREDENTIALS"))
        self.stdout.write("--------------------------------")

        self.stdout.write("Admin:       admin@lmsdemo.com / DemoAdmin123!")

        self.stdout.write(
            "Instructor:  john.instructor@lmsdemo.com / DemoInstructor123!"
        )

        self.stdout.write(
            "Instructor:  sarah.instructor@lmsdemo.com / DemoInstructor123!"
        )

        self.stdout.write("Students:    student1@lmsdemo.com - student5@lmsdemo.com")

        self.stdout.write("Password:    DemoStudent123!")
