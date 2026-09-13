from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, CourseViewSet, LessonViewSet

router = DefaultRouter()

router.register("courses", CourseViewSet, basename="course")
router.register("categories", CategoryViewSet, basename="category")
router.register("lessons", LessonViewSet, basename="lesson")
urlpatterns = router.urls
