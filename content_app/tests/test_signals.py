import os
from unittest.mock import patch, Mock
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from content_app.models import Video

# Diese Testklasse prüft das post_delete-Signal, das die Videodatei löscht.
@patch('content_app.signals.os.remove')
class TestFileDeletionSignals:
    """
    Tests für den post_delete Signal-Handler, der die physische Datei löscht.
    """
    def test_auto_delete_file_on_delete_with_file(self, mock_os_remove, db):
        """
        Testet, ob os.remove aufgerufen wird, wenn ein Video mit einer Datei gelöscht wird.
        """
        dummy_file_content = b"This is a dummy video file."
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            dummy_file_content,
            content_type="video/mp4"
        )
        
        # Erstelle ein Video-Objekt mit einer zugehörigen Datei
        video = Video.objects.create(title="Video to Delete", video_file=video_file)
        
        # Holen Sie sich den tatsächlichen Dateipfad, den der Signal-Handler empfängt
        file_path = video.video_file.path

        # Lösche die Modell-Instanz, was das Signal auslösen sollte
        video.delete()
        
        # Überprüfe, dass unser gemockter os.remove genau einmal mit dem korrekten Pfad aufgerufen wurde
        mock_os_remove.assert_called_once_with(file_path)

    def test_auto_delete_file_on_delete_no_file(self, mock_os_remove, db):
        """
        Testet, dass kein Dateilöschversuch unternommen wird, wenn kein video_file-Feld existiert.
        """
        # Erstelle ein Video ohne Datei
        video = Video.objects.create(title="Video without filefield")
        
        # Lösche die Modell-Instanz
        video.delete()
        
        # Überprüfe, dass os.remove nie aufgerufen wurde
        mock_os_remove.assert_not_called()

# Diese Testklasse prüft das post_save-Signal, das einen RQ-Job in die Warteschlange stellt.
# Wir patchen `django_rq.get_queue` und `Video.objects.get`, um die Logik zu isolieren.
@patch('content_app.signals.django_rq.get_queue')
class TestVideoPostSaveSignal:
    """
    Tests für den post_save Signal-Handler, der einen django-rq Job startet.
    """
    def test_video_post_save_new_video(self, mock_get_queue, db):
        """
        Testet, ob der `convert_480p`-Task in die Warteschlange gestellt wird,
        wenn ein neues Video mit einer Datei erstellt wird.
        """
        # Erstelle ein Mock für die Warteschlange
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        dummy_file = SimpleUploadedFile("dummy.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Test Video", description="A Test", video_file=dummy_file)
        
        # Überprüfe, dass `enqueue` genau einmal mit dem richtigen Task und Pfad aufgerufen wurde.
        mock_queue.enqueue.assert_called_once_with('content_app.tasks.convert_480p', video.video_file.path)

    @patch('content_app.signals.Video.objects.get')
    def test_video_post_save_existing_video_with_file_update(self, mock_get, mock_get_queue, db):
        """
        Testet, ob der `convert_480p`-Task in die Warteschlange gestellt wird,
        wenn die Videodatei eines bestehenden Videos aktualisiert wird.
        """
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        # Erstelle ein anfängliches Video mit einer Datei
        initial_file = SimpleUploadedFile("existing.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Existing Video", video_file=initial_file)
        
        # Setze den Mock von `enqueue` vom Erstellungsaufruf zurück
        mock_queue.enqueue.reset_mock()

        # Konfiguriere den Mock `get` so, dass er eine alte Video-Instanz mit dem ursprünglichen Pfad zurückgibt.
        # Dies ist notwendig, damit die Signallogik eine Dateiänderung erkennt.
        old_video_mock = Mock()
        old_video_mock.video_file.path = video.video_file.path
        mock_get.return_value = old_video_mock
        
        # Erstelle eine neue Datei, um die Aktualisierung zu simulieren
        updated_file = SimpleUploadedFile("updated.mp4", b"updated content", content_type="video/mp4")
        video.video_file = updated_file
        video.description = "Updated description"
        video.save()
        
        # Überprüfe, dass `enqueue` einmal mit dem Pfad der neuen Datei aufgerufen wurde
        mock_queue.enqueue.assert_called_once_with('content_app.tasks.convert_480p', video.video_file.path)

    @patch('content_app.signals.Video.objects.get')
    def test_video_post_save_existing_video_no_file_update(self, mock_get, mock_get_queue, db):
        """
        Testet, dass der `convert_480p`-Task NICHT in die Warteschlange gestellt wird,
        wenn ein bestehendes Video gespeichert wird, aber die Datei unverändert bleibt.
        """
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        # Erstelle ein anfängliches Video mit einer Datei
        initial_file = SimpleUploadedFile("existing.mp4", b"dummy content", content_type="video/mp4")
        video = Video.objects.create(title="Existing Video", video_file=initial_file)
        
        mock_queue.enqueue.reset_mock()

        # Konfiguriere den Mock `get` so, dass er eine alte Video-Instanz mit dem gleichen Pfad zurückgibt.
        old_video_mock = Mock()
        old_video_mock.video_file.path = video.video_file.path
        mock_get.return_value = old_video_mock
        
        # Ändere ein Feld, das nicht die Datei ist
        video.description = "Updated description"
        video.save()
        
        # Überprüfe, dass `enqueue` nicht aufgerufen wurde
        mock_queue.enqueue.assert_not_called()

    def test_video_post_save_no_file(self, mock_get_queue, db):
        """
        Testet, dass der `convert_480p`-Task NICHT aufgerufen wird, wenn kein Video-Datei-Feld vorhanden ist.
        """
        mock_queue = Mock()
        mock_get_queue.return_value = mock_queue

        video = Video.objects.create(title="Video without filefield")
        
        # Der Signal-Handler sollte den Conversion-Task nicht aufrufen
        mock_queue.enqueue.assert_not_called()





