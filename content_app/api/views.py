from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from content_app.models import Video
from content_app.api.serializers import VideoSerializer
from content_app.models import FileUpload
from .serializers import FileUploadSerializer

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