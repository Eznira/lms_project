from accounts.services.email_service import EmailService

from .models import Notification


class NotificationService:
    @staticmethod
    def create(
        *,
        recipient,
        notification_type,
        title,
        message,
        send_email=True,
    ):
        """
        Create an in-app notification and optionally
        send an email notification.
        """

        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
        )

        if send_email:
            EmailService.send_email(
                recipient=recipient.email,
                subject=title,
                message=message,
            )

        return notification

    # ---------------------------------------------
    # COURSE ENROLLMENT
    # ---------------------------------------------

    @staticmethod
    def enrollment_notification(student, course):

        return NotificationService.create(
            recipient=student,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title="Course Enrollment Successful",
            message=(f"You have successfully enrolled in the course '{course.title}'."),
        )

        # ---------------------------------------------

  
    # ---------------------------------------------
    # SUBMISSION
    # ---------------------------------------------
    @staticmethod
    def assignment_submission_notification_student(student, assignment):

        return NotificationService.create(
            recipient=student,
            notification_type=Notification.NotificationType.ASSIGNMENT_SUBMISSION,
            title="Assignment Submission Successful",
            message=(f"You have successfully submitted the assignment '{assignment.title}'."),
        )

    @staticmethod
    def assignment_submission_notification_instructor(instructor, student, assignment):

        return NotificationService.create(
            recipient=instructor,
            notification_type=Notification.NotificationType.ASSIGNMENT_SUBMISSION,
            title="New Assignment Submission",
            message=(f"Student '{student.first_name} {student.last_name}' has submitted the assignment '{assignment.title}'."),
        )

    @staticmethod
    def exam_submission_notification_student(student, examination):

        return NotificationService.create(
            recipient=student,
            notification_type=Notification.NotificationType.EXAM_SUBMISSION,
            title="Examination Submission Successful",
            message=(f"You have successfully submitted the examination '{examination.title}'."),
        )

    @staticmethod
    def exam_submission_notification_instructor(instructor, student, examination):

        return NotificationService.create(
            recipient=instructor,
            notification_type=Notification.NotificationType.EXAM_SUBMISSION,
            title="New Examination Submission",
            message=(f"Student '{student.first_name} {student.last_name}' has submitted the examination '{examination.title}'."),
        )
    
    # ---------------------------------------------
    # GRADE
    # ---------------------------------------------

    @staticmethod
    def grade_notification(
        student,
        item_name,
        score=None,
        feedback=None,
    ):

        if score is not None and feedback is not None:
            message = (
                f"Your grade for {item_name} has been published. Your score is {score}. Feedback: {feedback}"
            )
        elif score is not None:
            message = (
                f"Your grade for {item_name} has been published. Your score is {score}."
            )
        else:
            message = f"Your grade for {item_name} has been published."

        return NotificationService.create(
            recipient=student,
            notification_type=Notification.NotificationType.GRADE,
            title="Grade Published",
            message=message,
        )

    # ---------------------------------------------
    # CERTIFICATE
    # ---------------------------------------------

    @staticmethod
    def certificate_notification(student, course):

        return NotificationService.create(
            recipient=student,
            notification_type=Notification.NotificationType.CERTIFICATE,
            title="Certificate Available",
            message=(f"Your certificate for '{course.title}' is now available."),
        )

    # ---------------------------------------------
    # ASSIGNMENT REMINDER
    # ---------------------------------------------

    @staticmethod
    def assignment_reminder(student, assignment):

        return NotificationService.create(
            recipient=student,
            notification_type=(Notification.NotificationType.ASSIGNMENT_REMINDER),
            title="Assignment Reminder",
            message=(f"Reminder: the assignment '{assignment.title}' is due soon."),
        )

    # ---------------------------------------------
    # EXAM REMINDER
    # ---------------------------------------------

    @staticmethod
    def exam_reminder(student, examination):

        return NotificationService.create(
            recipient=student,
            notification_type=(Notification.NotificationType.EXAM_REMINDER),
            title="Examination Reminder",
            message=(f"Reminder: your examination '{examination.title}' is coming up."),
        )
