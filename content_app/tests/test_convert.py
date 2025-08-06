import os
from unittest.mock import patch, call
from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from content_app.models import Video
from content_app.tasks import convert_video_and_update_model  # Annahme: Dies ist die zu testende Funktion

# Testklasse für die Video-Konvertierungsaufgaben
# Wir patchen `subprocess.run`, um die eigentliche Ausführung von FFmpeg zu verhindern.
@patch('content_app.tasks.subprocess.run')
class VideoConversionTasksTest(TestCase):

    def setUp(self):
        """
        Einrichtung eines Video-Objekts und einer Dummy-Datei für die Tests.
        """
        # Erstelle ein temporäres Verzeichnis für die Dummy-Datei
        self.temp_media_root = os.path.join(settings.BASE_DIR, 'test_media')
        settings.MEDIA_ROOT = self.temp_media_root
        os.makedirs(os.path.join(self.temp_media_root, 'videos'), exist_ok=True)
        
        # Erstelle eine Dummy-Datei
        self.dummy_file_path = os.path.join(self.temp_media_root, 'videos', 'test_video.mp4')
        with open(self.dummy_file_path, 'wb') as f:
            f.write(b'dummy video content')

        # Erstelle eine Video-Instanz
        self.video = Video.objects.create(
            title="Test Video",
            video_file=os.path.join('videos', 'test_video.mp4')
        )

    def tearDown(self):
        """
        Bereinigung nach jedem Test.
        """
        # Lösche das temporäre Verzeichnis und alle Inhalte
        import shutil
        if os.path.exists(self.temp_media_root):
            shutil.rmtree(self.temp_media_root)
        
        # Setze MEDIA_ROOT auf den ursprünglichen Wert zurück (falls nötig)
        # Dies ist nur wichtig, wenn der ursprüngliche Wert benötigt wird
        # in anderen Tests, die nicht Teil dieser TestCase Klasse sind.
        # Im Rahmen einer vollständigen Testsuite sollte man dies global handhaben.
        
    def test_convert_480p_command_called_correctly(self, mock_subprocess_run):
        """
        Testet, ob die Konvertierung für 480p den korrekten FFmpeg-Befehl aufruft
        und das Modell aktualisiert.
        """
        target_resolution = 480
        expected_output_filename = "test_video_480p.mp4"
        expected_output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', f'{target_resolution}p')
        expected_output_path = os.path.join(expected_output_dir, expected_output_filename)

        # Der erwartete Befehl als Liste von Argumenten
        expected_command = [
            'ffmpeg', '-i', self.video.video_file.path,
            '-vf', f'scale=-2:{target_resolution}',
            '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '128k',
            '-strict', '-2',
            expected_output_path
        ]

        # Führe die zu testende Funktion aus
        convert_video_and_update_model(self.video.pk, target_resolution)

        # Überprüfe, dass `subprocess.run` genau einmal aufgerufen wurde
        mock_subprocess_run.assert_called_once()
        
        # Überprüfe, ob die Argumente des Aufrufs exakt mit dem erwarteten Befehl übereinstimmen
        mock_subprocess_run.assert_called_once_with(expected_command, check=True)

        # Überprüfe, ob das Modell aktualisiert wurde
        self.video.refresh_from_db()
        expected_relative_path = os.path.join('videos', f'{target_resolution}p', expected_output_filename)
        self.assertEqual(self.video.video_480p.name, expected_relative_path)
        
    def test_convert_720p_command_called_correctly(self, mock_subprocess_run):
        """
        Testet die Konvertierung für 720p.
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
        Testet, ob die Funktion os.makedirs aufruft, um die Verzeichnisse zu erstellen.
        """
        target_resolution = 480
        convert_video_and_update_model(self.video.pk, target_resolution)
        
        expected_output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', '480p')
        mock_makedirs.assert_called_once_with(expected_output_dir, exist_ok=True)

