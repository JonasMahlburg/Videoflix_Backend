import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
from .tasks import convert_480p, convert_720p, convert_1080p, generate_thumbnail
import django_rq
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Handles post-save signal for the Video model.

    If the instance is newly created, enqueue tasks to generate a thumbnail
    and convert the video into 480p, 720p, and 1080p resolutions.
    """
    if created:
        print(f'Starte Konvertierung für Video {instance.pk}')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue('content_app.tasks.generate_thumbnail', instance.pk)
        queue.enqueue(convert_480p, instance.pk)
        queue.enqueue(convert_720p, instance.pk)
        queue.enqueue(convert_1080p, instance.pk)
        

@receiver(post_delete, sender=Video)
def auto_delete_video_files(sender, instance, **kwargs):
    """
    Deletes all associated video files and the generated thumbnail after the Video model instance is deleted.
    """
    print(f'Lösche Dateien für Video {instance.pk}')
    
    file_fields = [
        instance.video_file,
        instance.video_480p,
        instance.video_720p,
        instance.video_1080p,
    ]

    # Thumbnail-URL in Dateipfad umwandeln und anhängen
    if instance.thumbnail_url:
        from django.conf import settings
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, instance.thumbnail_url)
        file_fields.append(thumbnail_path)
    
    for file_field in file_fields:
        # file_field kann ein FileField oder ein Pfadstring sein
        path = file_field.path if hasattr(file_field, 'path') else file_field
        if path and os.path.isfile(path):
            os.remove(path)
            print(f'Datei gelöscht: {path}')
        elif path:
            logger.warning(f"Datei nicht gefunden oder Pfad ungültig für Löschung: {path}")