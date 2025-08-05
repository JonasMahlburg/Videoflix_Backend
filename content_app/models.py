from django.db import models
from datetime import date

class Video(models.Model):
    """
    Represents a video uploaded to the platform.

    Includes metadata like title, description, and category,
    as well as fields for the original video file, converted versions,
    and a thumbnail URL.
    """
    title = models.CharField("Title", max_length=50)
    description = models.CharField("Description", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    video_480p = models.FileField(upload_to='videos/480p/', null=True, blank=True)
    video_720p = models.FileField(upload_to='videos/720p/', null=True, blank=True)
    video_1080p = models.FileField(upload_to='videos/1080p/', null=True, blank=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


class FileUpload(models.Model):
    """
    Handles general file uploads.

    Stores the uploaded file and the timestamp of the upload.
    """
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)