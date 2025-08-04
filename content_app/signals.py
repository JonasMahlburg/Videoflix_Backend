import os
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
from .tasks import convert_480p, convert_720p, convert_1080p
import django_rq


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print('New video created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        queue.enqueue(convert_720p, instance.video_file.path)
        queue.enqueue(convert_1080p, instance.video_file.path)
        

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

# logger = logging.getLogger(__name__)

# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     """
#     Signal handler that triggers a video conversion task when a video file is created or updated.
    
#     This handler now includes a check to ensure `instance.video_file` exists before
#     attempting to access its path, which prevents a ValueError.
#     """
#     logger.info("Video wurde gespeichert")
#     if instance.video_file:
#         # Check if the video_file has changed
#         try:
#             old_video = sender.objects.get(pk=instance.pk)
#             if old_video.video_file and old_video.video_file.path != instance.video_file.path:
#                 logger.info("Video file updated, starting conversion.")
#                 convert_480p.delay(instance.video_file.path)
#             elif created:
#                 logger.info("New video created, starting conversion.")
#                 convert_480p.delay(instance.video_file.path)
#             else:
#                 logger.info("Video saved, but file did not change. No conversion needed.")
#         except sender.DoesNotExist:
#             logger.info("New video created, starting conversion.")
#             convert_480p.delay(instance.video_file.path)
#     else:
#         logger.info("Video saved without a file. No conversion needed.")


# @receiver(post_delete, sender=Video)
# def auto_delete_file_on_delete(sender, instance, **kwargs):
#     """
#     Deletes the video file from the filesystem when the corresponding Video object is deleted.
    
#     This handler now checks if `instance.video_file` exists before attempting to delete it.
#     """
#     if instance.video_file:
#         if os.path.isfile(instance.video_file.path):
#             os.remove(instance.video_file.path)
#             logger.info(f"Deleted file: {instance.video_file.path}")
#         else:
#             logger.warning(f"File not found for deletion: {instance.video_file.path}")

