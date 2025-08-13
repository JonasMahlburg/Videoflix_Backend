import os
import shutil
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from content_app.models import Video
from content_app.tasks import convert_video_and_update_model

@patch('content_app.tasks.subprocess.run')
class VideoConversionTasksTest(TestCase):
    """
    Tests for video conversion tasks.

    This test suite verifies that FFmpeg is called with the correct arguments
    and that the video model is updated as expected.
    """

    def setUp(self):
        """
        Set up a video object and a dummy file for the tests.
        """
        self.temp_media_root = os.path.join(settings.BASE_DIR, 'test_media')
        settings.MEDIA_ROOT = self.temp_media_root
        os.makedirs(os.path.join(self.temp_media_root, 'videos'), exist_ok=True)
        
        self.dummy_file_path = os.path.join(self.temp_media_root, 'videos', 'test_video.mp4')
        with open(self.dummy_file_path, 'wb') as f:
            f.write(b'dummy video content')

        self.video = Video.objects.create(
            title="Test Video",
            video_file=os.path.join('videos', 'test_video.mp4')
        )

    def tearDown(self):
        """
        Clean up after each test.
        """
        if os.path.exists(self.temp_media_root):
            def onerror(func, path, exc_info):
                if issubclass(exc_info[0], OSError):
                    if os.path.islink(path):
                        os.unlink(path)
                    else:
                        raise
            
            try:
                shutil.onex(self.temp_media_root, onerror=onerror)
            except Exception as e:
                pass

    def test_convert_480p_command_called_correctly(self, mock_subprocess_run):
        """
        Tests if the 480p conversion calls the correct FFmpeg command and updates the model.
        """
        target_resolution = 480
        expected_output_filename = "test_video_480p.mp4"
        expected_output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', f'{target_resolution}p')
        expected_output_path = os.path.join(expected_output_dir, expected_output_filename)

        expected_command = [
            'ffmpeg', '-i', self.video.video_file.path,
            '-vf', f'scale=-2:{target_resolution}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '128k',
            '-strict', '-2',
            expected_output_path
        ]

        convert_video_and_update_model(self.video.pk, target_resolution)
        mock_subprocess_run.assert_called_once()
        mock_subprocess_run.assert_called_once_with(expected_command, check=True)

        self.video.refresh_from_db()
        expected_relative_path = os.path.join('videos', f'{target_resolution}p', expected_output_filename)
        self.assertEqual(self.video.video_480p.name, expected_relative_path)

    def test_convert_720p_command_called_correctly(self, mock_subprocess_run):
        """
        Tests if the 720p conversion calls the correct FFmpeg command and updates the model.
        """
        target_resolution = 720
        expected_output_filename = "test_video_720p.mp4"
        expected_output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', f'{target_resolution}p')
        expected_output_path = os.path.join(expected_output_dir, expected_output_filename)

        expected_command = [
            'ffmpeg', '-i', self.video.video_file.path,
            '-vf', f'scale=-2:{target_resolution}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '128k',
            '-strict', '-2',
            expected_output_path
        ]

        convert_video_and_update_model(self.video.pk, target_resolution)
        mock_subprocess_run.assert_called_once_with(expected_command, check=True)

        self.video.refresh_from_db()
        expected_relative_path = os.path.join('videos', f'{target_resolution}p', expected_output_filename)
        self.assertEqual(self.video.video_720p.name, expected_relative_path)

    @patch('content_app.tasks.os.makedirs')
    def test_convert_creates_directories_if_not_exist(self, mock_makedirs, mock_subprocess_run):
        """
        Tests if the function calls os.makedirs to create the necessary directories.
        """
        target_resolution = 480
        convert_video_and_update_model(self.video.pk, target_resolution)
        
        expected_output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', '480p')
        mock_makedirs.assert_called_once_with(expected_output_dir, exist_ok=True)

