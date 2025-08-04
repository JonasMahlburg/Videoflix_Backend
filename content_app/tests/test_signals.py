import os
import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from content_app.models import Video


# --- Pytest fixture for a temporary media directory ---
@pytest.fixture(scope='function')
def temp_media_root(tmp_path):
    """
    Creates a temporary media directory for tests to avoid
    affecting real files.
    """
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = tmp_path / "media_for_tests"
    settings.MEDIA_ROOT.mkdir()
    yield settings.MEDIA_ROOT
    settings.MEDIA_ROOT = original_media_root


# --- Tests for video_post_save ---
def test_video_post_save_new_video(capfd, db):
    """
    Tests that the correct messages are printed when a new video is created.
    'capfd' captures stdout/stderr. 'db' ensures the database is available.
    """
    Video.objects.create(title="Test Video", description="A Test")

    captured = capfd.readouterr()
    assert "Video wurde gespeichert" in captured.out
    assert "New video created" in captured.out


def test_video_post_save_existing_video(capfd, db):
    """
    Tests that only the "Video wurde gespeichert" message is printed
    when an existing video is updated.
    """
    video = Video.objects.create(title="Existing Video")


    capfd.readouterr()

    video.description = "Updated Description"
    video.save()


    captured = capfd.readouterr()

    assert "Video wurde gespeichert" in captured.out
    assert "New video created" not in captured.out


# --- Tests for auto_delete_file_on_delete ---

@patch('os.remove')
def test_auto_delete_file_on_delete_with_file(mock_os_remove, db, temp_media_root):
    """
    Tests if os.remove is called when a video with a file is deleted.
    """
    dummy_file_content = b"This is a dummy video file."
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        dummy_file_content,
        content_type="video/mp4"
    )

    video = Video.objects.create(
        title="Video to Delete",
        video_file=video_file
    )

    file_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(dummy_file_content)

    assert os.path.isfile(file_path)

    video.delete()

    mock_os_remove.assert_called_once_with(file_path)


@patch('os.path.isfile', return_value=False)
@patch('os.remove')
def test_auto_delete_file_on_delete_file_not_found(mock_os_remove, mock_os_path_isfile, db, temp_media_root):
    """
    Tests that os.remove is NOT called if the file is not found.
    """
    dummy_file_content = b"This is a dummy video file."
    video_file = SimpleUploadedFile(
        "non_existent_video.mp4",
        dummy_file_content,
        content_type="video/mp4"
    )

    video = Video.objects.create(
        title="Video without physical file",
        video_file=video_file
    )

    video.delete()

    mock_os_remove.assert_not_called()
    mock_os_path_isfile.assert_called_once()


def test_auto_delete_file_on_delete_no_file(db, temp_media_root):
    """
    Tests that no file deletion is attempted when no video_file exists.
    """
    with patch('os.remove') as mock_os_remove:
        video = Video.objects.create(title="Video without filefield")
        video.delete()
        mock_os_remove.assert_not_called()
