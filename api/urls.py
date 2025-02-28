from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register('courses', CourseViewSet)
router.register('lessons', LessonViewSet)
router.register('lesson-files', LessonFileViewSet)
router.register('comments', CommentViewSet)

urlpatterns = router.urls