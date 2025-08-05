from rest_framework import serializers
from core import settings
from content_app.models import Video, FileUpload

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']

class VideoSerializer(serializers.ModelSerializer):
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

        request = self.context.get('request')

  
        if obj.thumbnail_url:

            full_url = f"{request.build_absolute_uri('/')[:-1]}{settings.MEDIA_URL}{obj.thumbnail_url}"
            return full_url
        
        
        return None