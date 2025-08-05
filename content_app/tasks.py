import subprocess
import os
import logging
from django.conf import settings
from django_rq import job
from .models import Video

logger = logging.getLogger(__name__)

def get_filename_without_extension(file_path):
    """
    Extracts the filename from a path and removes its extension(s).
    Example: "/path/to/my_video.mp4" -> "my_video"
    Example: "/path/to/my_video.tar.gz" -> "my_video.tar" (if only the last is removed)
    To truly remove EVERYTHING after the first dot would be more complex,
    but for .mp4 os.path.splitext is sufficient.
    """
    base_name = os.path.basename(file_path)
    filename_without_ext, _ = os.path.splitext(base_name)
    return filename_without_ext


@job
def convert_video_and_update_model(video_pk, target_resolution):
    """
    Converts a video to a new resolution and saves the path in the model.
    This function is executed as an RQ task.
    """
    try:
        video_instance = Video.objects.get(pk=video_pk)
        original_path = video_instance.video_file.path
        
        filename_base = get_filename_without_extension(original_path)
        
        output_dir_absolute = os.path.join(settings.MEDIA_ROOT, 'videos', f'{target_resolution}p')
        os.makedirs(output_dir_absolute, exist_ok=True)

        target_filename = f"{filename_base}_{target_resolution}p.mp4"
        output_path_absolute = os.path.join(output_dir_absolute, target_filename)
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', original_path,
            '-vf', f'scale=-2:{target_resolution}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '128k',
            '-strict', '-2',
            output_path_absolute
        ]
        
        subprocess.run(ffmpeg_cmd, check=True)
        
        output_path_relative = os.path.join('videos', f'{target_resolution}p', target_filename)
        
        if target_resolution == 480:
            video_instance.video_480p.name = output_path_relative
        elif target_resolution == 720:
            video_instance.video_720p.name = output_path_relative
        elif target_resolution == 1080:
            video_instance.video_1080p.name = output_path_relative
        
        video_instance.save(update_fields=[f'video_{target_resolution}p'])
        logger.info(f"Video {video_pk} successfully converted to {target_resolution}p and model updated.")

    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_pk} not found for conversion.")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error during conversion of video {video_pk} to {target_resolution}p: {e}")
    except FileNotFoundError:
        logger.error("Error: ffmpeg command not found. Make sure ffmpeg is installed and in PATH.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during conversion for video {video_pk}: {e}")


def convert_480p(video_pk):
    return convert_video_and_update_model.delay(video_pk, 480)

def convert_720p(video_pk):
    return convert_video_and_update_model.delay(video_pk, 720)

def convert_1080p(video_pk):
    return convert_video_and_update_model.delay(video_pk, 1080)

def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
        logger.info(f"Deleted file: {path}")
    else:
        logger.warning(f"File not found for deletion: {path}")

def generate_thumbnail(video_pk):
    """
    Generates a thumbnail from a video (e.g., frame at second 1) and saves it under MEDIA_ROOT/thumbnails
    and updates the `thumbnail_url` field in the Video model.
    """
    try:
        video_instance = Video.objects.get(pk=video_pk)
        input_path = video_instance.video_file.path

        filename_base = get_filename_without_extension(input_path)
        
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        output_filename = f"{filename_base}_thumbnail.jpg"
        output_path = os.path.join(thumbnails_dir, output_filename)
        
        relative_path = os.path.join('thumbnails', output_filename)

        ffmpeg_cmd = [
            'ffmpeg',
            '-ss', '00:00:01',
            '-i', input_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        logger.info(f"Thumbnail successfully generated: {output_path}")

        video_instance.thumbnail_url = relative_path
        video_instance.save()
        logger.info(f"Video instance {video_pk} updated with thumbnail URL '{relative_path}'.")
        
    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_pk} not found for thumbnail generation.")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error while generating thumbnail for video {video_pk}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during thumbnail generation for video {video_pk}: {e}")