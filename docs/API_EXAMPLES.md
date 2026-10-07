# API Examples & Demo Workflow

These examples are written for the deployed LMS demo and use the seeded data created by `seed_demo`. IDs are intentionally represented by Postman collection variables because database IDs can differ between environments.

## Demo base URL

```text
https://lms-project-aj6m.onrender.com
```

Local development uses:

```text
http://127.0.0.1:8000
```

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | `admin@lmsdemo.com` | `DemoAdmin123!` |
| Instructor | `john.instructor@lmsdemo.com` | `DemoInstructor123!` |
| Instructor | `sarah.instructor@lmsdemo.com` | `DemoInstructor123!` |
| Student | `student1@lmsdemo.com` | `DemoStudent123!` |
| Student | `student2@lmsdemo.com` | `DemoStudent123!` |

Additional seeded students are `student3@lmsdemo.com`, `student4@lmsdemo.com`, and `student5@lmsdemo.com` with the same demo password.

## Seeded showcase data

The demo database contains:

- **Python Fundamentals** — published, instructor: John Okafor
- **Django REST API Development** — published, instructor: John Okafor
- **Flutter Mobile Development** — published, instructor: Sarah Eze
- **Database Fundamentals** — draft, instructor: Sarah Eze
- Lessons for each course
- Student enrollments and mixed lesson progress
- Assignments, submissions, quizzes, quiz attempts, examinations, and exam attempts
- A completed Python certificate for `student1`
- Reviews and notifications

The exact numeric IDs are environment-dependent. Use list requests to populate the corresponding Postman collection variables instead of hard-coding IDs.

---

## 1. Login

`POST /api/auth/login/`

```json
{
  "email": "admin@lmsdemo.com",
  "password": "DemoAdmin123!"
}
```

A successful response contains:

```json
{
  "refresh": "<refresh-token>",
  "access": "<access-token>"
}
```

For protected requests, send:

```text
Authorization: Bearer <access-token>
```

The Postman collection automatically saves both tokens as collection variables.

---

## 2. List courses

`GET /api/courses/`

The seeded catalog includes published courses visible to students and a draft course visible to instructors/admins according to the role rules.

Useful filters/search examples:

```text
GET /api/courses/?search=Python
GET /api/courses/?category={{category_id}}
GET /api/courses/?level=BEGINNER
```

After the list request, the Postman collection stores the first returned course ID in `{{course_id}}`.

---

## 3. Get a course

`GET /api/courses/{{course_id}}/`

Example response shape:

```json
{
  "id": 1,
  "title": "Python Fundamentals",
  "description": "...",
  "category": 1,
  "instructor": "john.instructor@lmsdemo.com",
  "duration": 8,
  "price": "0.00",
  "level": "BEGINNER",
  "status": "PUBLISHED"
}
```

The numeric values above are illustrative; use the IDs returned by the current environment.

---

## 4. List lessons for a course

`GET /api/lessons/?course={{course_id}}`

Students can access lessons for courses in which they are enrolled. Instructors can access lessons according to course ownership/visibility rules.

The collection stores the first lesson ID as `{{lesson_id}}`.

---

## 5. Complete a lesson as a student

`POST /api/lessons/{{lesson_id}}/complete/`

Authenticate as a student first. The student must be enrolled in the lesson's course.

A successful request creates or returns the student's lesson-completion record.

---

## 6. List enrollments

`GET /api/enrollments/`

When authenticated as `student1@lmsdemo.com`, the seeded data includes enrollments in:

- Python Fundamentals
- Django REST API Development

The first returned enrollment ID is stored as `{{enrollment_id}}` by the Postman collection.

---

## 7. Assignments and submissions

### List assignments

`GET /api/assignments/?course={{course_id}}`

Seeded assignment examples include:

- **Build a Calculator** — Python Fundamentals
- **Build a REST API** — Django REST API Development
- **Build a Course List App** — Flutter Mobile Development

### Submit an assignment

`POST /api/submissions/`

This endpoint accepts the assignment ID and a submission file.

```text
assignment = {{assignment_id}}
submission_file = <file>
```

### Grade a submission

`POST /api/submissions/{{submission_id}}/grade/`

```json
{
  "grade": 18,
  "feedback": "Good work! Well structured solution."
}
```

---

## 8. Quizzes

### List quizzes

`GET /api/quizzes/?course={{course_id}}`

Seeded quizzes include Python Fundamentals Quiz, Django REST API Quiz, and Flutter Fundamentals Quiz.

### Get quiz questions

`GET /api/quiz-questions/by-quiz/?quiz={{quiz_id}}`

The collection also provides the general quiz-question list endpoint.

### Start a quiz attempt

`POST /api/quiz-attempts/`

```json
{
  "quiz": {{quiz_id}}
}
```

### Submit a quiz attempt

`POST /api/quiz-attempts/{{quiz_attempt_id}}/submit/`

```json
{
  "answers": {
    "1": "B",
    "2": "A",
    "3": "C"
  }
}
```

Objective questions are automatically scored when the attempt is submitted.

---

## 9. Examinations

### List examinations

`GET /api/examinations/?course={{course_id}}`

The seeded data includes:

- **Python Final Examination** — completed historical attempt data
- **Django REST API Final Examination** — active demo examination

### Start an exam

`POST /api/exam-attempts/`

```json
{
  "examination": {{examination_id}}
}
```

### Submit an exam

`POST /api/exam-attempts/{{exam_attempt_id}}/submit/`

```json
{
  "answers": {
    "1": "B",
    "2": "TRUE",
    "3": "Serializers convert complex data types...",
    "4": "C"
  }
}
```

Objective questions are graded automatically. Essay questions can be graded separately by an instructor/admin.

### Grade an essay answer

`PATCH /api/exam-attempts/{{exam_attempt_id}}/grade/`

```json
{
  "question_id": {{exam_question_id}},
  "marks": 8
}
```

---

## 10. Grades and results

### Student grades

`GET /api/grades/`

Optional course filter:

```text
GET /api/grades/?course={{course_id}}
```

### Results

`GET /api/results/`

For instructor/admin course results:

```text
GET /api/results/?course={{course_id}}
```

---

## 11. Certificates

`GET /api/certificates/`

`student1@lmsdemo.com` has a seeded certificate for Python Fundamentals.

To issue a certificate as an instructor/admin:

`POST /api/certificates/`

```json
{
  "student": {{student_id}},
  "course": {{course_id}}
}
```

The completion percentage is calculated from the student's available graded learning activity when it is not supplied.

---

## 12. Reviews

### List reviews

`GET /api/reviews/`

### Create a review

Authenticate as a student and use a course in which the student is enrolled:

`POST /api/reviews/`

```json
{
  "course": {{course_id}},
  "rating": 5,
  "comment": "Excellent course with practical examples."
}
```

The Postman collection stores the first review ID as `{{review_id}}` when reviews are listed.

### Update a review

`PATCH /api/reviews/{{review_id}}/`

```json
{
  "rating": 4,
  "comment": "Updated review."
}
```

---

## 13. Notifications

`GET /api/notifications/`

The seeded demo includes notification records for learning activity such as enrollment and assessment events.

Mark one notification as read:

`POST /api/notifications/{{notification_id}}/mark-read/`

Check unread count:

`GET /api/notifications/unread-count/`

Mark all as read:

`POST /api/notifications/mark-all-read/`

---

## 14. Analytics

Student analytics:

`GET /api/analytics/student/`

Instructor analytics:

`GET /api/analytics/instructor/`

Admin analytics:

`GET /api/analytics/admin/`

Each endpoint enforces the corresponding role.

---

## Recommended demo sequence

For a clean presentation, use this order:

1. Open **Swagger UI** and show the API groups and JWT Authorize button.
2. Log in as `student1@lmsdemo.com`.
3. View the student's profile and enrolled courses.
4. Show Python lesson progress, quiz/exam activity, grades, and certificate.
5. Log in as `john.instructor@lmsdemo.com`.
6. Show instructor-owned courses and course-filtered assessments.
7. Show assignment grading or exam essay grading.
8. Log in as `admin@lmsdemo.com`.
9. Show unrestricted course/assessment visibility and admin analytics.
10. Use the Postman collection for repeatable request execution and automated response checks.

For the full request catalogue, see `LMS_API.postman_collection.json`. For collection-variable setup and execution details, see `docs/POSTMAN_GUIDE.md`.
