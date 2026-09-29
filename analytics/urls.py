from django.urls import path

from .views import AdminAnalyticsView, InstructorAnalyticsView, StudentAnalyticsView

urlpatterns = [
    path(
        "student/",
        StudentAnalyticsView.as_view(),
        name="student-analytics",
    ),
    path(
        "instructor/",
        InstructorAnalyticsView.as_view(),
        name="instructor-analytics",
    ),
    path("admin/", AdminAnalyticsView.as_view(), name="admin-analytics"),
]
