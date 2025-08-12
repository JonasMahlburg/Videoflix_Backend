Siehst du, so kommen wir der Sache näher. Die README.md soll also zwei Installationsmethoden beinhalten: eine für Docker und eine für die manuelle Python-Einrichtung. Außerdem muss die Docker-Anleitung so einfach wie möglich sein, damit auch Einsteiger sie verstehen.

Hier ist die überarbeitete README.md. Ich habe sie in zwei Hauptabschnitte für die Einrichtung unterteilt und die Docker-Anleitung mit noch einfacheren Erklärungen versehen.

🎬 Videoflix - Backend API
Ein robustes und skalierbares Backend für eine moderne Video-Streaming-Plattform, entwickelt mit Django, Django REST Framework, PostgreSQL und Redis (RQ). Es bietet eine umfassende API für Benutzerauthentifizierung, Video-Management, asynchrone Videoverarbeitung und HLS (HTTP Live Streaming).

✨ Features
Kernfunktionalität
🔐 Sichere Authentifizierung: Vollständiger Registrierungs- und Anmeldeprozess mit E-Mail-Bestätigung und sicherem, Cookie-basiertem JWT-Authentifizierungssystem (Access & Refresh Tokens).

🎞️ Asynchrone Videoverarbeitung: Hochgeladene Videos werden automatisch im Hintergrund verarbeitet, ohne die API zu blockieren.

🚀 HLS Adaptive Bitrate Streaming: Videos werden in verschiedene Auflösungen (1080p, 720p, 480p) konvertiert und als HLS-Streams (Playlist .m3u8 und Segmente .ts) bereitgestellt.

🖼️ Automatische Thumbnail-Erstellung: Für jedes Video wird automatisch ein Vorschaubild generiert.

✅ Umfassende API: Bietet Endpunkte für die Verwaltung und Bereitstellung von Videos und Streams.

Technische Merkmale
🐳 Containerisiert: Vollständig mit Docker und Docker Compose containerisiert für eine einfache Entwicklung und Bereitstellung.

🔄 Asynchrone Aufgabenwarteschlange: Nutzt Redis und django-rq zur Verarbeitung rechenintensiver Aufgaben wie Videokonvertierung.

🔧 Solides Backend: Basierend auf Django und dem Django REST Framework (DRF).

🗃️ PostgreSQL-Datenbank: Verwendet eine leistungsstarke und zuverlässige PostgreSQL-Datenbank.

🧪 Umfassend getestet: Enthält eine detaillierte Testsuite, um die Codequalität zu sichern.

⚙️ Umgebungsspezifische Konfiguration: Trennung von Code und Konfiguration durch .env-Dateien.

🛠️ Tech Stack
Backend: Django, Django REST Framework

Datenbank: PostgreSQL

Caching & Task Queue: Redis

Asynchrone Aufgaben: django-rq

Videoverarbeitung: FFmpeg

Containerisierung: Docker, Docker Compose

WSGI Server: Gunicorn

🚀 Getting Started
Es gibt zwei Wege, das Projekt aufzusetzen: mit Docker (empfohlen) oder manuell mit Python.

Methode 1: Projekt mit Docker aufsetzen (Empfohlen)
Docker macht die Einrichtung einfach, da es alle notwendigen Programme (wie Python, PostgreSQL und Redis) automatisch für dich installiert und konfiguriert. Du musst nur Docker Desktop installieren.

1. Voraussetzungen
Git: Zum Klonen des Projekts.

Docker Desktop: Enthält Docker und Docker Compose. Lade es hier herunter: Docker Desktop.
Starte Docker Desktop nach der Installation.

2. Projekt klonen
Öffne dein Terminal (oder die Kommandozeile) und gib diese Befehle ein:

Bash

git clone <REPO-URL>
cd <Projektordner>
3. Die .env-Datei vorbereiten
Im Hauptordner des Projekts gibt es eine Datei namens env.example. Sie enthält die Standardeinstellungen. Erstelle eine Kopie davon und nenne sie .env.

Bash

cp env.example .env
Öffne die neue .env-Datei in einem Texteditor. Die Standardwerte sind für die lokale Entwicklung in der Regel in Ordnung, du musst sie also nicht unbedingt ändern.

4. Docker-Container starten
Jetzt starten wir alle Teile des Projekts auf einmal. Dieser Befehl baut die Images (so etwas wie Vorlagen für die Programme), startet die Services (Web-API, Datenbank, Redis) und führt alle notwendigen Einrichtungsschritte aus (z. B. Datenbankmigrationen).

Bash

docker compose up --build
Tipp: Wenn du die Container im Hintergrund laufen lassen möchtest, verwende docker compose up --build -d.

Nach ein paar Minuten ist die Anwendung unter http://localhost:8000 erreichbar.

Methode 2: Manuelles Setup mit Python
Wenn du das Projekt ohne Docker direkt auf deinem Computer ausführen möchtest, folge dieser Anleitung.

1. Voraussetzungen
Python 3.10+: Stelle sicher, dass Python auf deinem System installiert ist.

PostgreSQL: Installiere und starte einen PostgreSQL-Datenbankserver.

Redis: Installiere und starte einen Redis-Server.

FFmpeg: Installiere FFmpeg, damit die Videoverarbeitung funktioniert.

2. Projekt klonen und einrichten
Öffne dein Terminal und führe diese Befehle aus:

Bash

git clone <REPO-URL>
cd <Projektordner>
Erstelle eine virtuelle Umgebung und aktiviere sie:

Bash

python -m venv venv
# Für Windows
.\venv\Scripts\activate
# Für macOS/Linux
source venv/bin/activate
3. Abhängigkeiten installieren
Installiere alle benötigten Python-Pakete aus der requirements.txt-Datei:

Bash

pip install -r requirements.txt
4. Die .env-Datei vorbereiten
Erstelle eine .env-Datei, wie in der Docker-Anleitung beschrieben. Die Werte für DB_HOST und REDIS_HOST müssen hier localhost sein.

# .env-Datei für manuelles Setup
DB_HOST=localhost
REDIS_HOST=localhost
... (restliche Einstellungen)
5. Datenbank migrieren und Superuser anlegen
Führe die Datenbankmigrationen aus und erstelle einen Admin-Benutzer:

Bash

python manage.py migrate
python manage.py createsuperuser
6. Server starten
Starte den Django-Entwicklungsserver und den RQ-Worker in zwei separaten Terminals:

Bash

# Terminal 1: Django-Server starten
python manage.py runserver

# Terminal 2: RQ-Worker starten
python manage.py rqworker
Die Anwendung ist jetzt unter http://localhost:8000 erreichbar.

📄 API-Übersicht
Das Projekt stellt folgende Haupt-Endpunkte zur Verfügung.

Methode	Pfad	Beschreibung
POST	/api/register/	Registrierung
POST	/api/login/	Login (JWT in Cookies)
POST	/api/logout/	Logout (Token-Blacklist, Cookies)
POST	/api/password_reset/	Passwort-Reset anfordern
POST	/api/password_confirm/<uid>/<token>/	Neues Passwort setzen
GET	/api/video/	Liste aller Videos
GET	/api/video/<id>/	Einzelnes Video
GET	/api/video/<id>/<auflösung>/index.m3u8	HLS Playlist für Video
GET	/api/video/<id>/<auflösung>/<segment>/	HLS Segment

In Google Sheets exportieren
🧪 Tests ausführen
Die gesamte Testsuite kann mit einem einzigen Befehl ausgeführt werden, während die Docker-Container laufen.

Bash

docker compose exec web python manage.py test
📝 Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die LICENSE-Datei für weitere Details.