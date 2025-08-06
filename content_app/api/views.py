from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from content_app.models import Video
from content_app.api.serializers import VideoSerializer
from content_app.models import FileUpload
from .serializers import FileUploadSerializer
from django.conf import settings
import os


class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer


class HLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        
        file_path = os.path.join(settings.MEDIA_ROOT, "hls", str(movie_id), resolution, "index.m3u8")

        if not os.path.exists(file_path):
            raise Http404("HLS Playlist not found")

        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')

class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        file_path = os.path.join(settings.MEDIA_ROOT, "hls", str(movie_id), resolution, segment)

        if not os.path.exists(file_path):
            raise Http404("Segment not found.")

        return FileResponse(open(file_path, 'rb'), content_type='video/MP2T')