import os
import shutil
from unittest.mock import patch, Mock, call
from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from content_app.models import Video
from content_app.tasks import (
    generate_thumbnail,
    generate_hls_playlist,
    convert_video_and_update_model
)


@patch('content_app.signals.delete_file')
@patch('content_app.signals.shutil.rmtree')
class TestFileDeletionSignals(TestCase):
    """
    Tests for the post_delete signal handler that deletes physical files.
    """
    def setUp(self):
        """
        Set up a temporary media root and a Video object for each test.
        """
        self.temp_media_root = os.path.join(settings.BASE_DIR, 'test_media')
        settings.MEDIA_ROOT = self.temp_media_root

        os.makedirs(os.path.join(self.temp_media_root, 'videos', '480p'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_media_root, 'videos', '720p'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_media_root, 'thumbnails'), exist_ok=True)

        self.video = Video.objects.create(
            title="Video to Delete",
            video_file=os.path.join('videos', 'original.mp4'),
            video_480p=os.path.join('videos', '480p', 'original_480p.mp4'),
            video_720p=os.path.join('videos', '720p', 'original_720p.mp4'),
            thumbnail_url=os.path.join('thumbnails', 'original_thumbnail.jpg')
        )

        with open(os.path.join(settings.MEDIA_ROOT, self.video.video_file.name), 'w') as f: f.write('original')
        with open(os.path.join(settings.MEDIA_ROOT, self.video.video_480p.name), 'w') as f: f.write('480p')
        with open(os.path.join(settings.MEDIA_ROOT, self.video.video_720p.name), 'w') as f: f.write('720p')
        with open(os.path.join(settings.MEDIA_ROOT, self.video.thumbnail_url), 'w') as f: f.write('thumb')

    def tearDown(self):
        """
        Clean up the temporary media root after each test.
        """
        if os.path.exists(self.temp_media_root):
            shutil.rmtree(self.temp_media_root)

    def test_auto_delete_file_on_delete_with_files(self, mock_rmtree, mock_delete_file):
        """
        Tests that delete_file is called for all associated files when a Video is deleted.
        """
        expected_calls = [
            call(self.video.video_file.path),
            call(self.video.video_480p.path),
            call(self.video.video_720p.path),
            call(os.path.join(settings.MEDIA_ROOT, self.video.thumbnail_url))
        ]

        hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(self.video.pk))
        os.makedirs(hls_dir, exist_ok=True)
        
        self.video.delete()
        
        self.assertCountEqual(mock_delete_file.call_args_list, expected_calls)

        mock_rmtree.assert_called_once_with(hls_dir)


@patch('content_app.signals.django_rq.get_queue')
class TestVideoPostSaveSignal(TestCase):
    """
    Tests for the post_save signal handler that starts a django-rq job.
    """
    def setUp(self):
        """
        Set up a temporary media root for each test.
        """
        self.temp_media_root = os.path.join(settings.BASE_DIR, 'test_media')
        settings.MEDIA_ROOT = self.temp_media_root
        os.makedirs(self.temp_media_root, exist_ok=True)

    def tearDown(self):
        """
        Clean up the temporary media root after each test.
        """
        if os.path.exists(self.temp_media_root):
            shutil.rmtree(self.temp_media_root)

    def test_video_post_save_new_video(self, mock_get_queue):
        """
        Tests that the conversion tasks are enqueued when a new video with a file is created.
        """
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        dummy_file = SimpleUploadedFile("dummy.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Test Video", description="A Test", video_file=dummy_file)

        expected_calls = [
            call.enqueue(generate_thumbnail, video.pk),
            call.enqueue(convert_video_and_update_model, video.pk, 480),
            call.enqueue(convert_video_and_update_model, video.pk, 720),
            call.enqueue(convert_video_and_update_model, video.pk, 1080),
            call.enqueue(generate_hls_playlist, video.pk, 480),
            call.enqueue(generate_hls_playlist, video.pk, 720),
            call.enqueue(generate_hls_playlist, video.pk, 1080),
        ]
        
        mock_queue.assert_has_calls(expected_calls, any_order=True)

    def test_video_post_save_no_file(self, mock_get_queue):
        """
        Tests that no tasks are enqueued when a new video is created without a file.
        """
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        Video.objects.create(title="Video without filefield")

        mock_queue.enqueue.assert_not_called()
