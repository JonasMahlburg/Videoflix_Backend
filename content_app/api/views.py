from rest_framework import viewsets
from content_app.models import Video
from content_app.api.serializers import VideoSerializer

class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer