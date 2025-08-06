from django.urls import path, include
from rest_framework.routers import DefaultRouter
from content_app.api.views import VideoViewSet, HLSPlaylistView, HLSSegmentView

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video')


urlpatterns = [
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', HLSPlaylistView.as_view(), name='hls_playlist'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='hls_segment')
]

urlpatterns += router.urls
  
