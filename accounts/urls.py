from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import RegisterView

# from .views import InstructorTestView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),


    # # Test view to get the current logged-in user's information
    # path("me/", MeView.as_view(), name="me"),
    # # Test view for instructor permission
    # path("instructor-test/", InstructorTestView.as_view(), name="instructor-test"),
]

