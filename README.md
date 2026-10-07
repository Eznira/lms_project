# Education LMS API

A role-aware Learning Management System REST API built with Django REST Framework. The API supports authentication, course delivery, enrollments, lessons, assignments, quizzes, examinations, grading, certificates, reviews, notifications, and role-specific analytics.

**Live demo:** https://lms-project-aj6m.onrender.com

The deployed demo runs on Render and uses PostgreSQL in production. The repository also includes a local SQLite development setup and a seeded demo-data command for repeatable demonstrations.

## Highlights

- Custom email-based user authentication
- Student, instructor, and administrator roles
- JWT authentication with refresh tokens and refresh-token blacklisting on logout
- Email verification and password-reset flows
- Instructor onboarding controlled by administrators
- Course/category/lesson management
- Course enrollment and lesson completion tracking
- Assignments, file submissions, grading, and feedback
- Quizzes with timed attempts and automatic objective grading
- Scheduled examinations with MCQ, true/false, and essay questions
- Manual grading for examination essay questions
- Aggregated grades and course-level results
- Certificate issuance based on graded course work
- Course reviews and rating summaries
- In-app notifications and read-state actions
- Student, instructor, and administrator analytics
- Search, filtering, and ordering on supported resources
- OpenAPI schema, Swagger UI, and ReDoc documentation
- Postman collection with collection-variable automation

## Technology stack

| Component | Version |
|---|---:|
| Python | 3.14.x |
| Django | 6.1 |
| Django REST Framework | 3.18.0 |
| Simple JWT | 5.5.1 |
| drf-spectacular | 0.30.0 |
| django-filter | 26.1 |
| Pillow | 12.3.0 |
| django-cors-headers | 4.9.0 |
| python-decouple | 3.8 |
| Database | SQLite locally; PostgreSQL on the Render deployment |

Exact package versions are pinned in `requirements.txt`.

## Project structure

```text
lms_project/
├── accounts/          # Users, roles, profiles, authentication
├── analytics/         # Student/instructor/admin analytics
├── assessments/       # Assignments, quizzes, exams, grades, certificates
├── courses/           # Categories, courses, lessons
├── enrollments/       # Enrollments and lesson completion
├── notifications/     # In-app notifications
├── reviews/           # Course reviews and rating summaries
├── config/             # Django project configuration and URL routing
├── docs/
│   ├── API_EXAMPLES.md
│   ├── ERD.md
│   ├── ERD.svg
│   ├── ERD.dot
│   └── POSTMAN_GUIDE.md
├── samples/            # Small local fixtures for Postman file uploads
├── LMS_API.postman_collection.json
├── manage.py
├── requirements.txt
└── .env.example
```

## Architecture at a glance

```text
Client
  │
  ├── Swagger UI / ReDoc
  ├── Postman
  └── Web / Mobile application
          │
          ▼
     Django REST API
          │
    ┌─────┼───────────────────────────────┐
    │     │                               │
 accounts courses/enrollments       assessments
    │     │                               │
    └─────┴──────────────┬────────────────┘
                         │
                  notifications/reviews
                         │
                         ▼
                    Database + Media
```

The application uses Django apps to separate major business domains. DRF serializers define request/response representations and validation; viewsets/APIViews implement endpoint behavior; permission classes enforce role/ownership rules.

## Roles

### Student

Students can:

- register publicly
- verify their email
- log in and refresh JWT tokens
- view published courses
- enroll in courses
- access lessons for enrolled courses
- mark lessons as completed
- submit assignments
- attempt quizzes and examinations
- view their grades/results/certificates
- review enrolled courses
- view and manage their notifications
- access student analytics

### Instructor

Instructors can:

- authenticate after administrator-controlled onboarding
- manage their own courses
- manage lessons belonging to their courses
- create and manage assignments, quizzes, examinations, and questions for their courses
- view submissions for their courses
- grade assignment submissions
- manually grade examination essay questions
- view grades/results for their courses
- issue certificates for students in their courses when the certificate requirements are met
- access instructor analytics

### Administrator

Administrators can:

- manage instructors
- manage categories
- manage all courses and learning content
- view and manage enrollments
- manage assessments and grading
- issue/manage certificates
- manage reviews and notifications where the relevant permissions allow it
- access platform-wide analytics

## Authentication

The API uses JWT bearer authentication.

### Login

```http
POST /api/auth/login/
Content-Type: application/json
```

Example request:

```json
{
  "email": "student1@lmsdemo.com",
  "password": "DemoStudent123!"
}
```

For the deployed demo, use the credentials in the [Demo accounts](#demo-accounts) section below.

The response contains an access token and refresh token. Send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

### Refresh

```http
POST /api/auth/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "<refresh-token>"
}
```

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "refresh": "<refresh-token>"
}
```

Logout blacklists the supplied refresh token.

## Authentication lifecycle

### Student registration

```text
Register
   ↓
Verification email
   ↓
Verify email
   ↓
Account activated
   ↓
Login
   ↓
JWT access + refresh tokens
```

Public registration creates a `STUDENT` account. Public clients cannot select `INSTRUCTOR` or `ADMIN` during registration.

### Instructor onboarding

```text
Administrator creates instructor
          ↓
Verification/setup token
          ↓
Instructor sets password
          ↓
Account activated
          ↓
Instructor login
```

## Environment configuration

Create a local `.env` file from `.env.example`.

```env
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

Do **not** commit `.env` or real credentials to source control.

The included settings also support:

```text
BACKEND_URL=http://127.0.0.1:8000
```

`BACKEND_URL` defaults to the local development URL if it is not supplied.

## Installation

### 1. Clone the project

```bash
git clone <repository-url>
cd lms_project
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` using `.env.example` and provide the email settings required by the authentication flows.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

The custom user model uses email as the login identifier.

### 7. Seed demo data (optional)

To populate a local database with the same type of realistic demo data used by the deployed showcase, run:

```bash
python manage.py seed_demo --reset
```

This creates demo users, courses, lessons, enrollments, assignments, quizzes, examinations, certificates, reviews, notifications, and related records. The command resets the existing demo records before recreating them.

### 8. Start the development server

```bash
python manage.py runserver
```

The default development server is:

```text
http://127.0.0.1:8000/
```

## Deployed demo

The production demo is available at:

```text
https://lms-project-aj6m.onrender.com
```

### Demo accounts

These accounts are seeded specifically for demonstration and API testing:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@lmsdemo.com` | `DemoAdmin123!` |
| Instructor | `john.instructor@lmsdemo.com` | `DemoInstructor123!` |
| Instructor | `sarah.instructor@lmsdemo.com` | `DemoInstructor123!` |
| Student | `student1@lmsdemo.com` | `DemoStudent123!` |
| Student | `student2@lmsdemo.com` | `DemoStudent123!` |
| Student | `student3@lmsdemo.com` | `DemoStudent123!` |
| Student | `student4@lmsdemo.com` | `DemoStudent123!` |
| Student | `student5@lmsdemo.com` | `DemoStudent123!` |

The seeded data is intentionally varied so the API can be demonstrated from different roles: completed learning, partial progress, assignments, quizzes, examinations, certificates, reviews, notifications, instructor-owned courses, and admin-wide access.

### Production API documentation

- **Swagger UI:** https://lms-project-aj6m.onrender.com/api/docs/
- **ReDoc:** https://lms-project-aj6m.onrender.com/api/redoc/
- **OpenAPI schema:** https://lms-project-aj6m.onrender.com/api/schema/

For a guided demo workflow and concrete request/response examples, see [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md). For the Postman collection setup and recommended execution order, see [`docs/POSTMAN_GUIDE.md`](docs/POSTMAN_GUIDE.md).

## API documentation

For local development:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

For the deployed demo, use the production documentation links in [Deployed demo](#deployed-demo).

Swagger UI provides interactive API documentation and request execution. ReDoc provides a reading-oriented view of the same OpenAPI schema. The schema is generated by drf-spectacular.

## API endpoint overview

The API currently exposes 56 unique URL paths and more than 100 operations when CRUD methods and custom actions are counted.

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register/` | Register a student |
| POST | `/api/auth/verify-email/` | Verify email |
| POST | `/api/auth/login/` | Obtain JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| POST | `/api/auth/password-reset/` | Request password reset |
| POST | `/api/auth/password-reset-confirm/` | Confirm password reset |
| POST | `/api/auth/instructors/` | Create instructor |
| POST | `/api/auth/instructors/set-password/` | Set instructor password |

### Profile

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/profile/` | Get authenticated user profile |
| PATCH | `/api/profile/` | Update authenticated user profile |

### Courses and learning content

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/courses/` | List/create courses |
| GET/PUT/PATCH/DELETE | `/api/courses/{id}/` | Retrieve/update/delete course |
| GET/POST | `/api/categories/` | List/create categories |
| GET/PUT/PATCH/DELETE | `/api/categories/{id}/` | Retrieve/update/delete category |
| GET/POST | `/api/lessons/` | List/create lessons |
| GET/PUT/PATCH/DELETE | `/api/lessons/{id}/` | Retrieve/update/delete lesson |
| POST | `/api/lessons/{id}/complete/` | Complete lesson as an enrolled student |
| GET/POST/DELETE | `/api/enrollments/` | List/create/delete enrollments |
| GET/DELETE | `/api/enrollments/{id}/` | Retrieve/delete enrollment |

### Assignments and submissions

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/assignments/` | List/create assignments |
| GET/PUT/PATCH/DELETE | `/api/assignments/{id}/` | Manage assignment |
| POST | `/api/submissions/` | Submit assignment |
| GET | `/api/submissions/` | List submissions visible to current user |
| GET/PATCH/DELETE | `/api/submissions/{id}/` | Retrieve/resubmit/delete submission |
| POST | `/api/submissions/{id}/grade/` | Grade assignment submission |

### Quizzes

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/quizzes/` | List/create quizzes |
| GET/PUT/PATCH/DELETE | `/api/quizzes/{id}/` | Manage quiz |
| GET | `/api/quizzes/{id}/questions/` | List questions for a quiz |
| GET/POST | `/api/quiz-questions/` | List/create quiz questions |
| GET/PUT/PATCH/DELETE | `/api/quiz-questions/{id}/` | Manage quiz question |
| GET/POST | `/api/quiz-attempts/` | List/start quiz attempts |
| GET | `/api/quiz-attempts/{id}/` | Retrieve quiz attempt |
| POST | `/api/quiz-attempts/{id}/submit/` | Submit quiz attempt |

### Examinations

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/examinations/` | List/create examinations |
| GET/PUT/PATCH/DELETE | `/api/examinations/{id}/` | Manage examination |
| GET | `/api/examinations/{id}/questions/` | List examination questions |
| GET/POST | `/api/exam-questions/` | List/create examination questions |
| GET/PUT/PATCH/DELETE | `/api/exam-questions/{id}/` | Manage examination question |
| GET/POST | `/api/exam-attempts/` | List/start examination attempts |
| GET | `/api/exam-attempts/{id}/` | Retrieve examination attempt |
| POST | `/api/exam-attempts/{id}/submit/` | Submit examination attempt |
| PATCH | `/api/exam-attempts/{id}/grade/` | Manually grade examination question |

### Grades and results

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/grades/` | Aggregate assignment, quiz, and examination grades |
| GET | `/api/results/` | Calculate course results |
| GET | `/api/results/?course={id}` | Filter results by course |

For quizzes and examinations, the grade endpoint uses the highest submitted attempt for each student/assessment combination.

### Certificates

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/certificates/` | List/issue certificates |
| GET/PUT/PATCH/DELETE | `/api/certificates/{id}/` | Manage certificate |

Certificates calculate completion from graded assignments plus the highest submitted quiz/examination attempts for the course.

### Reviews

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/reviews/` | List/create reviews |
| GET/PATCH/DELETE | `/api/reviews/{id}/` | Retrieve/update/delete review |
| GET | `/api/reviews/course/{course_id}/summary/` | Average rating and review count |

Students must be enrolled in a course before reviewing it and can create only one review per course.

### Notifications

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/notifications/` | List notifications |
| GET | `/api/notifications/{id}/` | Retrieve notification |
| POST | `/api/notifications/{id}/mark-read/` | Mark one notification read |
| POST | `/api/notifications/mark-all-read/` | Mark all notifications read |
| GET | `/api/notifications/unread-count/` | Count unread notifications |

### Analytics

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/analytics/student/` | Student learning analytics |
| GET | `/api/analytics/instructor/` | Instructor course analytics |
| GET | `/api/analytics/admin/` | Platform-wide analytics |

## Filtering, search, and ordering

Supported resources use DRF's filter, search, and ordering backends where configured.

### Courses

Filters:

```text
?category=1
?category__slug=programming
?level=BEGINNER
?status=PUBLISHED
```

Search:

```text
?search=python
```

Ordering:

```text
?ordering=title
?ordering=-price
?ordering=-created_at
```

### Lessons

```text
?course=1
?search=variables
?ordering=order
```

### Assignments

```text
?course=1
?search=python
?ordering=-due_date
```

### Quizzes

```text
?course=1
?search=python
?ordering=-created_at
```

### Examinations

```text
?course=1
?status=SCHEDULED
?search=python
?ordering=start_time
```

### Reviews

```text
?course=1
?rating=5
?search=excellent
?ordering=-created_at
```

## Postman

Import:

```text
LMS_API.postman_collection.json
```

The collection is deliberately environment-free. All runtime state is stored in collection variables.

### Automatic variables

Login scripts save:

```text
access_token
refresh_token
current_role
```

Create requests save resource IDs such as:

```text
category_id
course_id
lesson_id
enrollment_id
assignment_id
submission_id
quiz_id
quiz_question_id
quiz_attempt_id
examination_id
exam_question_id
exam_attempt_id
certificate_id
notification_id
review_id
```

See [`docs/POSTMAN_GUIDE.md`](docs/POSTMAN_GUIDE.md) for the recommended execution order and file-upload workflow.

See [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md) for the request bodies captured from the Postman collection.

## Testing

The repository contains Django test-module placeholders for the major apps, but automated test coverage has not yet been implemented. The test suite can still be invoked with:

```bash
python manage.py test
```

Tests are a planned follow-up rather than a claim of current coverage.

## Database and media

Local development uses SQLite (`db.sqlite3`). The Render deployment uses PostgreSQL through `DATABASE_URL`.

Uploaded files are stored under `media/` in local development. The current demo deployment is intended for API demonstration rather than as a production file-storage architecture; a production application should use durable object/file storage for uploaded media.

## ER diagram

See:

- [`docs/ERD.md`](docs/ERD.md) — Mermaid source and relationship notes
- [`docs/ERD.svg`](docs/ERD.svg) — rendered ER diagram
- [`docs/ERD.dot`](docs/ERD.dot) — Graphviz source

![LMS ERD](docs/ERD.svg)

## Deployment notes

The deployed demo is configured with production-oriented settings including `DEBUG=False`, environment-based secrets, HTTPS redirects, secure cookies, HSTS, WhiteNoise static-file handling, and PostgreSQL through Render's `DATABASE_URL`.

For a new production deployment, review the following before exposing the API publicly:

- set a strong `SECRET_KEY` through environment variables
- configure `ALLOWED_HOSTS` and CORS for the intended domains
- use PostgreSQL or another production database
- use durable object/file storage for uploaded media
- configure production email delivery
- review JWT lifetimes and refresh-token blacklisting requirements
- run `python manage.py check --deploy`
- never commit `.env` or real credentials

The demo credentials in this README are intentionally public and should not be reused for a real application.

## API documentation philosophy

The OpenAPI documentation is generated from the actual Django/DRF implementation. `drf-spectacular` inspects serializers, viewsets, APIViews, authentication, filters, and explicit `@extend_schema` metadata.

The project uses explicit schema metadata where business behavior is not obvious from the Python method signature, especially for:

- authentication flows
- role-specific operations
- custom actions such as lesson completion and assessment submission
- custom grading/results endpoints
- request examples
- response descriptions

## Development commands

```bash
# Run server
python manage.py runserver

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Run tests
python manage.py test

# Check deployment configuration
python manage.py check --deploy
```


## License

Add the project's chosen license here before publishing the repository.

## Maintainer

Arinze Ihim
