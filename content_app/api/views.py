from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from content_app.models import Video
from content_app.api.serializers import VideoSerializer
from .serializers import FileUploadSerializer
from django.conf import settings
import os


class FileUploadView(APIView):
    def post(self, request, format=None):
        """
        Handles the POST request to upload a file.

        The method validates the uploaded data using FileUploadSerializer.
        If the data is valid, a new FileUpload instance is created and saved.
        
        Args:
            request (Request): The incoming request object.
            format (str, optional): The format of the request. Defaults to None.

        Returns:
            Response: A Response object containing the serializer data if successful
                      (HTTP 201), or serializer errors if the data is invalid
                      (HTTP 400).
        """
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for displaying Video instances.

    It provides 'list' and 'retrieve' actions. The queryset is ordered
    by the creation date in descending order.
    """
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer


class HLSPlaylistView(APIView):
    """
    View to serve the HLS playlist file (.m3u8) for a video.
    
    This view ensures that the requested file exists and returns it as a
    FileResponse with the appropriate content type.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """
        Handles the GET request to retrieve the HLS playlist file.
        
        Args:
            request (Request): The incoming request object.
            movie_id (int): The primary key of the Video instance.
            resolution (str): The desired video resolution (e.g., '480p').

        Returns:
            FileResponse: The HLS playlist file if found.

        Raises:
            Http404: If the specified playlist file does not exist.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, "hls", str(movie_id), resolution, "index.m3u8")

        if not os.path.exists(file_path):
            raise Http404("HLS Playlist not found")

        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    """
    View to serve individual HLS video segments (.ts).
    
    This view provides access to the video segments that make up an HLS stream.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """
        Handles the GET request for a specific HLS video segment.
        
        Args:
            request (Request): The incoming request object.
            movie_id (int): The primary key of the Video instance.
            resolution (str): The video resolution of the segment.
            segment (str): The filename of the video segment.

        Returns:
            FileResponse: The video segment file if found.

        Raises:
            Http404: If the specified segment file does not exist.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, "hls", str(movie_id), resolution, segment)

        if not os.path.exists(file_path):
            raise Http404("Segment not found.")

        return FileResponse(open(file_path, 'rb'), content_type='video/MP2T')
    