import os
from unittest.mock import patch, Mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import pytest

from content_app.models import Video

# We need to patch both `os.remove` and `convert_480p` in this test suite
# because creating a video instance triggers the post_save signal.
@patch('content_app.signals.os.remove')
@patch('content_app.signals.convert_480p')
class TestFileDeletionSignals:
    """
    Tests for the post_delete signal handler.
    """
    def test_auto_delete_file_on_delete_with_file(self, mock_convert_480p, mock_os_remove, db):
        """
        Tests if os.remove is called when a video with a file is deleted.
        """
        dummy_file_content = b"This is a dummy video file."
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            dummy_file_content,
            content_type="video/mp4"
        )
        
        video = Video.objects.create(title="Video to Delete", video_file=video_file)
        
        # Get the actual path that the signal handler will receive
        file_path = video.video_file.path

        # Delete the model instance, which should trigger the signal
        video.delete()
        
        # Assert that our mocked os.remove was called once with the correct path
        mock_os_remove.assert_called_once_with(file_path)
        
        # Check that the post_save signal did run during the create() call
        mock_convert_480p.delay.assert_called_once()

    def test_auto_delete_file_on_delete_no_file(self, mock_convert_480p, mock_os_remove, db):
        """
        Tests that no file deletion is attempted when no video_file exists.
        """
        video = Video.objects.create(title="Video without filefield")
        
        # Delete the model instance
        video.delete()
        
        # Assert that os.remove was never called
        mock_os_remove.assert_not_called()
        
        # Check that the post_save signal did not run during the create() call
        mock_convert_480p.delay.assert_not_called()

@patch('content_app.signals.convert_480p')
class TestVideoPostSaveSignal:
    """
    Tests for the post_save signal handler.
    """
    def test_video_post_save_new_video(self, mock_convert_480p, db):
        """
        Tests that the convert_480p task is called when a new video with a file is created.
        """
        dummy_file = SimpleUploadedFile("dummy.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Test Video", description="A Test", video_file=dummy_file)
        
        # Assert that the delay method of our mock was called once with the video's file path
        mock_convert_480p.delay.assert_called_once_with(video.video_file.path)

    @patch('content_app.signals.Video.objects.get')
    def test_video_post_save_existing_video(self, mock_get, mock_convert_480p, db):
        """
        Tests that the convert_480p task is called when an existing video is updated.
        
        We mock `Video.objects.get` to simulate the video's state before the update,
        allowing the signal handler to correctly detect a file change.
        """
        # Create an initial video with a file
        dummy_file = SimpleUploadedFile("existing.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Existing Video", video_file=dummy_file)
        
        # Reset the conversion mock from the create call
        mock_convert_480p.delay.reset_mock()

        # Configure the mock `get` to return an old video instance with the original path
        old_video_mock = Mock()
        old_video_mock.video_file.path = video.video_file.path
        mock_get.return_value = old_video_mock
        
        # Create a new file to simulate the update
        updated_file = SimpleUploadedFile("updated.mp4", b"updated content", content_type="video/mp4")
        video.video_file = updated_file
        video.description = "Updated description"
        video.save()
        
        # Assert that the mock was called once with the path of the *new* file
        mock_convert_480p.delay.assert_called_once_with(video.video_file.path)

    def test_video_post_save_no_file(self, mock_convert_480p, db):
        """
        Tests that the convert_480p task is NOT called if no video file is provided.
        """
        video = Video.objects.create(title="Video without filefield")
        
        # The signal handler should not call the conversion task
        mock_convert_480p.delay.assert_not_called()

    def test_video_post_save_with_no_file_update(self, mock_convert_480p, db):
        """
        Tests that the conversion task is NOT called if the video file field is not changed.
        """
        dummy_file = SimpleUploadedFile("no_update.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="No Update Test", video_file=dummy_file)
        
        mock_convert_480p.delay.reset_mock()
        
        video.description = "Just a description update"
        video.save()
        
        mock_convert_480p.delay.assert_not_called()





