from django.db import models
from datetime import date



class Video(models.Model):
    title = models.CharField("Title", max_length=50)
    description = models.CharField("Description", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=50)


#-----------------------------Video Model aus Videos ----------------------------------

# class Video(models.Model):
#     created_at = models.DateField(default=date.today)
#     title = models.CharField(max_length=80)
#     description = models.CharField(max_length=500)
#     video_file = models.FileField(upload_to='videos', blank=True, null=True)

#     def __str__(self):
#         return self.title