from rest_framework import serializers
from content_app.models import Video, FileUpload

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'