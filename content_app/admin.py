from django.contrib import admin
from .models import Video

# Register your models here.

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "created_at")
    search_fields = ("title", "category")
    list_filter = ("category", "created_at")
    ordering = ("-created_at",)


