import pytest
import subprocess
import os
from unittest.mock import patch
from content_app.tasks import convert_480p

@pytest.fixture
def mock_subprocess_run():
    """
    Mockt subprocess.run, um zu verhindern, dass echte ffmpeg-Befehle ausgeführt werden.
    Gibt ein MagicMock-Objekt zurück, das inspiziert werden kann.
    """
    with patch('subprocess.run') as mock_run:
        yield mock_run

@pytest.fixture
def dummy_source_file(tmp_path):
    """
    Erstellt eine temporäre Dummy-Quelldatei für den Test.
    """
    source_file = tmp_path / "test_source.mp4"
    source_file.touch() 
    return str(source_file)

def test_convert_480p_command_called_correctly(mock_subprocess_run, dummy_source_file):
    """
    Testet, ob convert_480p den korrekten ffmpeg-Befehl als Liste aufruft.
    """
    source = dummy_source_file
    expected_target = source + '_480p.mp4'

    # Der erwartete Befehl wird jetzt als Liste von Argumenten definiert
    expected_command = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        expected_target
    ]

    convert_480p(source)

    # Überprüfe, ob subprocess.run genau einmal aufgerufen wurde
    mock_subprocess_run.assert_called_once()
    
    # Überprüfe, ob die Argumentliste des Aufrufs exakt mit der erwarteten Liste übereinstimmt.
    # mock_subprocess_run.call_args ist ein Tupel, dessen erstes Element (index 0) 
    # die Positionsargumente enthält. Das erste Positionsargument (index 0) ist unsere Liste.
    assert mock_subprocess_run.call_args[0][0] == expected_command

    # Optional: Überprüfe, ob die Zieldatei nicht tatsächlich erstellt wurde,
    # da subprocess.run gemockt ist.
    assert not os.path.exists(expected_target)

# Ein weiterer Testfall, falls die Quelle ein Leerzeichen enthält (was oft Probleme macht)
def test_convert_480p_with_space_in_source(mock_subprocess_run, tmp_path):
    """
    Testet die Konvertierung, wenn der Quellpfad Leerzeichen enthält.
    """
    source_with_space = tmp_path / "my test source.mp4"
    source_with_space.touch()
    source_path_str = str(source_with_space)
    expected_target = source_path_str + '_480p.mp4'

    # Der erwartete Befehl als Liste von Argumenten
    expected_command = [
        'ffmpeg',
        '-i', source_path_str,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        expected_target
    ]

    convert_480p(source_path_str)

    mock_subprocess_run.assert_called_once()
    assert mock_subprocess_run.call_args[0][0] == expected_command

