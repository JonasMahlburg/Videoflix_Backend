import os
import shutil
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import django_rq
from .models import Video
from .tasks import generate_thumbnail, convert_video_and_update_model, generate_hls_playlist, delete_file

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Triggers asynchronous tasks for video processing after a new video is created.
    """
    if created and instance.video_file:
        print(f'Starting conversion for Video {instance.pk}')
        queue = django_rq.get_queue('default')

        queue.enqueue(generate_thumbnail, instance.pk)
        queue.enqueue(convert_video_and_update_model, instance.pk, 480)
        queue.enqueue(convert_video_and_update_model, instance.pk, 720)
        queue.enqueue(convert_video_and_update_model, instance.pk, 1080)
        queue.enqueue(generate_hls_playlist, instance.pk, 480)
        queue.enqueue(generate_hls_playlist, instance.pk, 720)
        queue.enqueue(generate_hls_playlist, instance.pk, 1080)


@receiver(post_delete, sender=Video)
def auto_delete_video_files(sender, instance, **kwargs):
    """
    Deletes all related video files and directories when a Video instance is deleted.
    """
    print(f'Deleting files for Video {instance.pk}')
    
    file_fields = [
        instance.video_file,
        instance.video_480p,
        instance.video_720p,
        instance.video_1080p,
    ]
    
    for file_field in file_fields:
        if file_field and file_field.name:
            file_path = file_field.path
            delete_file(file_path)

    if instance.thumbnail_url:
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, instance.thumbnail_url)
        delete_file(thumbnail_path)

    hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(instance.pk))
    if os.path.exists(hls_dir):
        shutil.rmtree(hls_dir)
        print(f"HLS directory deleted: {hls_dir}")