from rest_framework import serializers
from core import settings
from content_app.models import Video, FileUpload


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for the FileUpload model.

    This serializer is used for handling file uploads, validating the
    uploaded file, and storing it with its upload timestamp.
    """
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.

    This serializer is used to provide a read-only representation of
    the Video model, including a dynamically generated thumbnail URL.
    """
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category'
        ]

    def get_thumbnail_url(self, obj):
        """
        Generates the full absolute URL for the video's thumbnail.

        This method checks if a thumbnail URL exists for the given video
        object and, if so, constructs a complete URL by prepending the
        current request's base URI and the MEDIA_URL setting.

        Args:
            obj (Video): The Video instance being serialized.

        Returns:
            str or None: The full URL to the thumbnail, or None if no
                         thumbnail URL is set on the object.
        """
        request = self.context.get('request')
        
        if obj.thumbnail_url:
            full_url = (f"{request.build_absolute_uri('/')[:-1]}"
                        f"{settings.MEDIA_URL}{obj.thumbnail_url}")
            return full_url

        return None
    