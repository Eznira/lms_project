# LMS Entity Relationship Diagram

The diagram below reflects the Django models currently implemented in the project. `User` is the central identity model; course content, enrollment, assessment, notification, review, and certificate records reference it directly or indirectly.

```mermaid
erDiagram
    USER ||--o| STUDENT_PROFILE : has
    USER ||--o| INSTRUCTOR_PROFILE : has
    USER ||--o{ EMAIL_VERIFICATION_TOKEN : receives
    USER ||--o{ COURSE : instructs
    CATEGORY ||--o{ COURSE : contains
    COURSE ||--o{ LESSON : contains
    USER ||--o{ ENROLLMENT : makes
    COURSE ||--o{ ENROLLMENT : has
    USER ||--o{ LESSON_COMPLETION : records
    LESSON ||--o{ LESSON_COMPLETION : has
    COURSE ||--o{ ASSIGNMENT : contains
    ASSIGNMENT ||--o{ ASSIGNMENT_SUBMISSION : receives
    USER ||--o{ ASSIGNMENT_SUBMISSION : submits
    COURSE ||--o{ QUIZ : contains
    QUIZ ||--o{ QUIZ_QUESTION : contains
    QUIZ ||--o{ QUIZ_ATTEMPT : has
    USER ||--o{ QUIZ_ATTEMPT : makes
    COURSE ||--o{ EXAMINATION : contains
    EXAMINATION ||--o{ EXAM_QUESTION : contains
    EXAMINATION ||--o{ EXAM_ATTEMPT : has
    USER ||--o{ EXAM_ATTEMPT : makes
    USER ||--o{ CERTIFICATE : earns
    COURSE ||--o{ CERTIFICATE : awards
    USER ||--o{ REVIEW : writes
    COURSE ||--o{ REVIEW : receives
    USER ||--o{ NOTIFICATION : receives

    USER {
        int id PK
        string email UK
        string role
        boolean email_verified
    }
    STUDENT_PROFILE {
        int id PK
        int user_id FK UK
        string phone
        text biography
        image profile_photo
    }
    INSTRUCTOR_PROFILE {
        int id PK
        int user_id FK UK
        string qualification
        string specialization
        text biography
        string phone
        image profile_photo
    }
    EMAIL_VERIFICATION_TOKEN {
        int id PK
        int user_id FK
        uuid token UK
        datetime created_at
        datetime expires_at
    }
    CATEGORY {
        int id PK
        string name UK
        string slug UK
        text description
        datetime created_at
    }
    COURSE {
        int id PK
        int category_id FK
        int instructor_id FK
        string title
        text description
        int duration
        decimal price
        string level
        image thumbnail
        string status
        datetime created_at
        datetime updated_at
    }
    LESSON {
        int id PK
        int course_id FK
        string title
        text content
        file video
        file pdf
        file audio
        string external_resource
        int order
        datetime created_at
        datetime updated_at
    }
    ENROLLMENT {
        int id PK
        int student_id FK
        int course_id FK
        datetime enrolled_at
    }
    LESSON_COMPLETION {
        int id PK
        int student_id FK
        int lesson_id FK
        datetime completed_at
    }
    ASSIGNMENT {
        int id PK
        int course_id FK
        string title
        text description
        datetime due_date
        int total_marks
        file attachment
        datetime created_at
        datetime updated_at
    }
    ASSIGNMENT_SUBMISSION {
        int id PK
        int assignment_id FK
        int student_id FK
        file submission_file
        datetime submitted_at
        int grade
        text feedback
    }
    QUIZ {
        int id PK
        int course_id FK
        string title
        text description
        int duration
        datetime created_at
        datetime updated_at
    }
    QUIZ_QUESTION {
        int id PK
        int quiz_id FK
        text question_text
        string question_type
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_answer
        int marks
        int order
    }
    QUIZ_ATTEMPT {
        int id PK
        int quiz_id FK
        int student_id FK
        json answers
        int score
        int total_marks
        datetime started_at
        datetime submitted_at
    }
    EXAMINATION {
        int id PK
        int course_id FK
        string title
        text description
        int duration
        datetime start_time
        datetime end_time
        string status
        datetime created_at
        datetime updated_at
    }
    EXAM_QUESTION {
        int id PK
        int examination_id FK
        text question_text
        string question_type
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_answer
        int marks
        int order
    }
    EXAM_ATTEMPT {
        int id PK
        int examination_id FK
        int student_id FK
        json answers
        json manual_grades
        int score
        int total_marks
        datetime started_at
        datetime submitted_at
    }
    CERTIFICATE {
        int id PK
        int student_id FK
        int course_id FK
        string certificate_number UK
        decimal completion_percentage
        datetime issued_at
    }
    REVIEW {
        int id PK
        int student_id FK
        int course_id FK
        int rating
        text comment
        datetime created_at
        datetime updated_at
    }
    NOTIFICATION {
        int id PK
        int recipient_id FK
        string notification_type
        string title
        text message
        boolean is_read
        datetime created_at
    }
```

## Important constraints

- A student can enroll in a course only once.
- A student can complete a lesson only once.
- A student can submit an assignment only once under the database uniqueness constraint.
- A student can review a course only once.
- A student can receive only one certificate per course.
- Lesson order is unique within a course.
- Quiz-question order is unique within a quiz.
- Examination-question order is unique within an examination.
- Course categories use unique names and slugs.
