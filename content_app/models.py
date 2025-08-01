from django.db import models
from datetime import date

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    title = models.CharField("Title", max_length=50)
    description = models.CharField("Description", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)


    def __str__(self):
        return self.title
