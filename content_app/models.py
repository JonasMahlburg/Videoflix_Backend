from django.db import models

class Video(models.Model):
    title = models.CharField("Title", max_length=50)
    description = models.CharField("Description", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=50)