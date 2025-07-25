from django.urls import path, include
from rest_framework.routers import DefaultRouter
from content_app.api.views import VideoViewSet

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video')

urlpatterns = router.urls
  
