# API Request Examples

These examples are synchronized from `LMS_API.postman_collection.json`. Replace collection variables with values from your local run where necessary.

## Auth / Register

`POST {{base_url}}/api/auth/register/`

```json
{
  "email": "student@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "StrongPassword123!",
  "password_confirm": "StrongPassword123!"
}
```

## Auth / Verify Email

`POST {{base_url}}/api/auth/verify-email/`

```json
{
  "token": "your-verification-token-here"
}
```

## Auth / Login

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{student1_email}}",
  "password": "{{student1_password}}"
}
```

## Auth / Refresh Token

`POST {{base_url}}/api/auth/refresh/`

```json
{
  "refresh": "{{refresh_token}}"
}
```

## Auth / Logout

`POST {{base_url}}/api/auth/logout/`

```json
{
  "refresh": "{{refresh_token}}"
}
```

## Auth / Password Reset

`POST {{base_url}}/api/auth/password-reset/`

```json
{
  "email": "student@example.com"
}
```

## Auth / Password Reset Confirm

`POST {{base_url}}/api/auth/password-reset-confirm/`

```json
{
  "uid": "encoded-uid",
  "token": "reset-token",
  "new_password": "NewStrongPassword123!",
  "new_password_confirm": "NewStrongPassword123!"
}
```

## Auth / Create Instructors

`POST {{base_url}}/api/auth/instructors/`

```json
{
  "email": "instructor@example.com",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

## Auth / Set Instructor Password

`POST {{base_url}}/api/auth/instructors/set-password/`

```json
{
  "token": "instructor-setup-token",
  "new_password": "InstructorPass123!",
  "new_password_confirm": "InstructorPass123!"
}
```

## Auth / Login - Admin

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{admin_email}}",
  "password": "{{admin_password}}"
}
```

## Auth / Login - Instructor

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{instructor_email}}",
  "password": "{{instructor_password}}"
}
```

## Auth / Login - Student

`POST {{base_url}}/api/auth/login/`

```json
{
  "email": "{{student1_email}}",
  "password": "{{student1_password}}"
}
```

## Course / Create Course

`POST {{base_url}}/api/courses/`

```json
{
  "title": "Python Basics",
  "description": "Introduction to Python programming",
  "category": {{category_id}},
  "duration": 30,
  "price": "49.99",
  "level": "BEGINNER",
  "status": "DRAFT"
}
```

## Course / Update Course - Put

`PUT {{base_url}}/api/courses/{{course_id}}/`

```json
{
  "title": "Python Basics Updated",
  "description": "Updated introduction to Python programming",
  "category": {{category_id}},
  "duration": 40,
  "price": "59.99",
  "level": "BEGINNER",
  "status": "PUBLISHED"
}
```

## Course / Update Course - Patch

`PATCH {{base_url}}/api/courses/{{course_id}}/`

```json
{
  "status": "PUBLISHED"
}
```

## Category / Create Category

`POST {{base_url}}/api/categories/`

```json
{
  "name": "Programming",
  "description": "Courses related to programming and software development"
}
```

## Category / Update Category - Put

`PUT {{base_url}}/api/categories/{{category_id}}/`

```json
{
  "name": "Programming Updated",
  "description": "Updated description for programming courses"
}
```

## Category / Update Category - Patch

`PATCH {{base_url}}/api/categories/{{category_id}}/`

```json
{
  "description": "Partially updated description"
}
```

## Profile / Update User Profile

`PATCH {{base_url}}/api/profile/`

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "phone": "+1234567890",
    "biography": "A passionate learner."
  }
}
```

## Lesson / Create Lesson

`POST {{base_url}}/api/lessons/`

```json
{
  "course": {{course_id}},
  "title": "Introduction to Variables",
  "content": "In this lesson, we cover Python variables and data types.",
  "order": 1
}
```

## Lesson / Update Lesson - Put

`PUT {{base_url}}/api/lessons/{{lesson_id}}/`

```json
{
  "course": {{course_id}},
  "title": "Introduction to Variables - Updated",
  "content": "Updated content for Python variables and data types.",
  "order": 1
}
```

## Lesson / Update Lesson - Patch

`PATCH {{base_url}}/api/lessons/{{lesson_id}}/`

```json
{
  "content": "Partially updated lesson content."
}
```

## Enrollment / Enroll in Course

`POST {{base_url}}/api/enrollments/`

```json
{
  "course": {{course_id}}
}
```

## Assignment / Create Assignment

`POST {{base_url}}/api/assignments/`

```json
{
  "course": {{course_id}},
  "title": "Python Variables Assignment",
  "description": "Write a Python script demonstrating variable usage.",
  "due_date": "2027-01-01T23:59:00Z",
  "total_marks": 100
}
```

## Assignment / Create Assignment With Attachment

`POST {{base_url}}/api/assignments/`

| Field | Type | Example |
|---|---|---|
| `course` | `text` | `{{course_id}}` |
| `title` | `text` | `Assignment With File` |
| `description` | `text` | `Assignment that includes an attachment file.` |
| `due_date` | `text` | `2027-01-01T23:59:00Z` |
| `total_marks` | `text` | `100` |
| `attachment` | `file` | `{{attachment_file_path}}` |

## Assignment / Update Assignment - Put

`PUT {{base_url}}/api/assignments/{{assignment_id}}/`

```json
{
  "course": {{course_id}},
  "title": "Python Variables Assignment Updated",
  "description": "Updated assignment description.",
  "due_date": "2027-02-01T23:59:00Z",
  "total_marks": 100
}
```

## Assignment / Update Assignment - Patch

`PATCH {{base_url}}/api/assignments/{{assignment_id}}/`

```json
{
  "description": "Partially updated assignment description."
}
```

## Submission / Submit Assignment

`POST {{base_url}}/api/submissions/`

| Field | Type | Example |
|---|---|---|
| `assignment` | `text` | `{{assignment_id}}` |
| `submission_file` | `file` | `{{submission_file_path}}` |

## Submission / Resubmit Assignment

`PATCH {{base_url}}/api/submissions/{{submission_id}}/`

```json
{
  "submission_file": "{{submission_file_path}}"
}
```

## Submission / Grade Assignment

`POST {{base_url}}/api/submissions/{{submission_id}}/grade/`

```json
{
  "grade": 85,
  "feedback": "Good work! Well structured solution."
}
```

## Quiz / Create Quiz

`POST {{base_url}}/api/quizzes/`

```json
{
  "course": {{course_id}},
  "title": "Python Basics Quiz",
  "description": "Test your knowledge of Python basics.",
  "duration": 30
}
```

## Quiz / Update Quiz

`PUT {{base_url}}/api/quizzes/{{quiz_id}}/`

```json
{
  "course": {{course_id}},
  "title": "Python Basics Quiz Updated",
  "description": "Updated quiz description.",
  "duration": 45
}
```

## Quiz / Partial Update Quiz

`PATCH {{base_url}}/api/quizzes/{{quiz_id}}/`

```json
{
  "duration": 60
}
```

## Quiz-attempt / Start Quiz

`POST {{base_url}}/api/quiz-attempts/`

```json
{
  "quiz": {{quiz_id}}
}
```

## Quiz-attempt / Submit Quiz

`POST {{base_url}}/api/quiz-attempts/{{quiz_attempt_id}}/submit/`

```json
{
  "answers": {
    "1": "b",
    "2": "a"
  }
}
```

## Quiz-questions / Create Quiz Questions

`POST {{base_url}}/api/quiz-questions/`

```json
{
  "quiz": {{quiz_id}},
  "question_text": "What is the correct way to declare a variable in Python?",
  "question_type": "MCQ",
  "option_a": "var x = 5",
  "option_b": "x = 5",
  "option_c": "int x = 5",
  "option_d": "declare x = 5",
  "correct_answer": "B",
  "marks": 1,
  "order": 1
}
```

## Quiz-questions / Update Question

`PUT {{base_url}}/api/quiz-questions/{{quiz_question_id}}/`

```json
{
  "quiz": {{quiz_id}},
  "question_text": "Updated: What is the correct way to declare a variable in Python?",
  "question_type": "MCQ",
  "option_a": "var x = 5",
  "option_b": "x = 5",
  "option_c": "int x = 5",
  "option_d": "declare x = 5",
  "correct_answer": "B",
  "marks": 1,
  "order": 1
}
```

## Quiz-questions / Partial Update Question

`PATCH {{base_url}}/api/quiz-questions/{{quiz_question_id}}/`

```json
{
  "correct_answer": "B"
}
```

## Examination / Create Examination

`POST {{base_url}}/api/examinations/`

```json
{
  "course": {{course_id}},
  "title": "Python Final Exam",
  "description": "Comprehensive exam covering all Python topics.",
  "duration": 120,
  "start_time": "2027-01-15T09:00:00Z",
  "end_time": "2027-01-15T11:00:00Z"
}
```

## Examination / Update Examination

`PUT {{base_url}}/api/examinations/{{examination_id}}/`

```json
{
  "course": {{course_id}},
  "title": "Python Final Exam Updated",
  "description": "Updated comprehensive exam.",
  "duration": 150,
  "start_time": "2027-01-20T09:00:00Z",
  "end_time": "2027-01-20T11:30:00Z"
}
```

## Examination / Partial Update Examination

`PATCH {{base_url}}/api/examinations/{{examination_id}}/`

```json
{
  "status": "ONGOING"
}
```

## Examination-questions / Create Exam Question

`POST {{base_url}}/api/exam-questions/`

```json
{
  "examination": {{examination_id}},
  "question_text": "Explain the concept of object-oriented programming in Python.",
  "question_type": "ESSAY",
  "marks": 20,
  "order": 1
}
```

## Examination-questions / Update Exam Question

`PUT {{base_url}}/api/exam-questions/{{exam_question_id}}/`

```json
{
  "examination": {{examination_id}},
  "question_text": "Updated: Explain OOP in Python with examples.",
  "question_type": "ESSAY",
  "marks": 25,
  "order": 1
}
```

## Examination-questions / Partial Update Exam Question

`PATCH {{base_url}}/api/exam-questions/{{exam_question_id}}/`

```json
{
  "marks": 30
}
```

## Exam-attempt / Start Exam

`POST {{base_url}}/api/exam-attempts/`

```json
{
  "examination": {{examination_id}}
}
```

## Exam-attempt / Submit Exam

`POST {{base_url}}/api/exam-attempts/{{exam_attempt_id}}/submit/`

```json
{
  "answers": {
    "1": "This is my essay answer about OOP in Python.",
    "2": "b"
  }
}
```

## Exam-attempt / Essay Grading

`PATCH {{base_url}}/api/exam-attempts/{{exam_attempt_id}}/grade/`

```json
{
  "question_id": {{exam_question_id}},
  "marks": 18
}
```

## Certificate / Create Certificate

`POST {{base_url}}/api/certificates/`

```json
{
  "student": "{{student_id}}",
  "course": "{{course_id}}"
}
```

## Certificate / Update Certificate - Put

`PUT {{base_url}}/api/certificates/{{certificate_id}}/`

```json
{
  "student": "{{student_id}}",
  "course": "{{course_id}}"
}
```

## Certificate / Update Certificate - Patch

`PATCH {{base_url}}/api/certificates/{{certificate_id}}/`

```json
{
  "course": "{{course_id}}"
}
```

## Reviews / Create Review

`POST {{base_url}}/api/reviews/`

```json
{
  "course": "{{course_id}}",
  "rating": 5,
  "comment": "Excellent course."
}
```

## Reviews / Update Review

`PATCH {{base_url}}/api/reviews/{{review_id}}/`

```json
{
  "rating": 4,
  "comment": "Updated review."
}
```
