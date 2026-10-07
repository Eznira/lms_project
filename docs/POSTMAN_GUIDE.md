# Postman Guide

The LMS project includes a ready-to-run Postman collection: `LMS_API.postman_collection.json`.

The collection is designed around **collection variables only**. You do not need to import or configure a Postman environment.

## 1. Import the collection

In Postman:

1. Select **Import**.
2. Choose `LMS_API.postman_collection.json`.
3. Open the imported `LMS_API` collection.
4. Open the collection's **Variables** tab.

The collection is already configured with the deployed demo URL.

```text
base_url = https://lms-project-aj6m.onrender.com
```

For local development, change only `base_url`:

```text
base_url = http://127.0.0.1:8000
```

## 2. Demo credential variables

The credential variables are intentionally kept in the collection:

| Variable | Demo value |
|---|---|
| `admin_demo` | `admin@lmsdemo.com` |
| `instructor1_demo` | `john.instructor@lmsdemo.com` |
| `instructor2_demo` | `sarah.instructor@lmsdemo.com` |
| `student1_demo` | `student1@lmsdemo.com` |
| `student2_demo` | `student2@lmsdemo.com` |
| `password_demo` | Change to the password for the role you are logging in as |

Passwords:

```text
Admin:       DemoAdmin123!
Instructors: DemoInstructor123!
Students:    DemoStudent123!
```

The collection deliberately keeps one password variable so the login requests can be switched between the seeded roles without creating a Postman environment.

## 3. Authentication workflow

The Auth folder contains three ready-made login requests:

- **Login - Admin** → `{{admin_demo}}`
- **Login - Instructor** → `{{instructor1_demo}}`
- **Login - Student** → `{{student1_demo}}`

Before running an instructor or student login, set `password_demo` to that role's seeded password.

A successful login automatically stores:

```text
access_token
refresh_token
```

as **collection variables**.

Protected requests use the collection-level Bearer authentication configuration, so you normally do not need to paste tokens manually.

## 4. Resource IDs are also collection variables

The collection uses variables for generated resource IDs instead of hard-coded IDs.

Examples:

```text
course_id
category_id
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
review_id
notification_id
student_id
user_id
```

List/profile requests capture useful IDs into these variables automatically when the response contains the relevant records.

For example, **List Courses** saves the first course ID as:

```text
{{course_id}}
```

You can then call:

```text
GET {{base_url}}/api/courses/{{course_id}}/
```

## 5. Recommended execution order

For a fresh collection, use this sequence:

### Student flow

1. **Auth → Login - Student**
2. **Profile → Get User Profile**
3. **Course → List Courses**
4. **Course → Get Course**
5. **Lesson → List Lessons**
6. **Enrollment → List Enrollments**
7. **Assignment → List Assignments**
8. **Quiz → List Quizzes**
9. **Quiz-attempt → List Quiz Attempts**
10. **Examination → List Examinations**
11. **Certificate → List Certificates**
12. **Notifications → List Notification**
13. **Reviews → List Reviews**
14. **Analytics → Student Analytics**

This is primarily a read/demo flow and is safe for presenting the seeded dataset.

### Instructor flow

1. **Auth → Login - Instructor**
2. **Profile → Get User Profile**
3. **Course → List Courses**
4. **Course → Get Course**
5. **Assignment → List Assignments**
6. **Quiz → List Quizzes**
7. **Quiz-questions → List Quiz Questions**
8. **Examination → List Examinations**
9. **Examination-questions → List Exam Questions**
10. **Submission → List Submissions**
11. **Grade → List Grades**
12. **Results → Results by Course**
13. **Analytics → Instructor Analytics**

### Admin flow

1. **Auth → Login - Admin**
2. **Category → List Categories**
3. **Course → List Courses**
4. **Assignment → List Assignments**
5. **Quiz → List Quizzes**
6. **Examination → List Examinations**
7. **Certificate → List Certificates**
8. **Notifications → List Notification**
9. **Reviews → List Reviews**
10. **Analytics → Admin Analytics**

## 6. Write operations

Create/update/delete requests are included for the complete API workflow, but use them deliberately against the seeded demo database.

Examples:

```text
POST /api/courses/
POST /api/assignments/
POST /api/quizzes/
POST /api/examinations/
POST /api/enrollments/
POST /api/reviews/
```

A successful create request saves its returned ID into the corresponding collection variable where supported.

For example, creating a course updates:

```text
course_id
```

and creating a quiz updates:

```text
quiz_id
```

## 7. File uploads

Assignment and lesson endpoints that accept files are included in the collection.

For file-upload requests, select the appropriate local file in Postman before sending the request. File paths are intentionally not hard-coded because they differ between machines.

## 8. Token refresh and logout

Use **Auth → Refresh Token** when the access token expires.

The request uses:

```json
{
  "refresh": "{{refresh_token}}"
}
```

The refreshed access token is saved back into the collection variable automatically.

Use **Auth → Logout** to blacklist the refresh token. After logout, run a login request again before calling protected endpoints.

## 9. Collection variables vs environment variables

This collection intentionally uses:

```javascript
pm.collectionVariables.set("access_token", json.access);
```

instead of:

```javascript
pm.collectionVariables.set("access_token", json.access);
```

Therefore:

- No Postman environment is required.
- Tokens stay with the imported collection.
- Generated IDs stay with the imported collection.
- The collection can be exported/imported as one self-contained demo artifact.

## 10. Troubleshooting

### `401 Unauthorized`

Run the appropriate login request again. Check that `access_token` contains a current token.

### `403 Forbidden`

The endpoint is working, but the logged-in role does not have permission. Switch to the required demo role.

### `404 Not Found`

Check that the URL has exactly one slash between the host and `/api`:

```text
https://lms-project-aj6m.onrender.com/api/...
```

not:

```text
https://lms-project-aj6m.onrender.com//api/...
```

### Empty resource variable

Run the corresponding list/create request first. For example, run **List Courses** before using `{{course_id}}`.

### Local requests fail

Make sure Django is running:

```bash
python manage.py runserver
```

and that `base_url` is:

```text
http://127.0.0.1:8000
```

## 11. Swagger vs Postman

Use **Swagger UI** for interactive API exploration, authentication, schemas, and quick individual requests.

Use **Postman** for repeatable workflows, role switching, file uploads, collection variables, and automated response assertions.

Production documentation:

- Swagger UI: `https://lms-project-aj6m.onrender.com/api/docs/`
- ReDoc: `https://lms-project-aj6m.onrender.com/api/redoc/`
- OpenAPI schema: `https://lms-project-aj6m.onrender.com/api/schema/`
