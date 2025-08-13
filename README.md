# 🎬 Videoflix - Backend API

Ein robustes und skalierbares Backend für eine moderne Video-Streaming-Plattform, entwickelt mit Django, Django REST Framework, PostgreSQL und Redis (RQ). Es bietet eine umfassende API für Benutzerauthentifizierung, Video-Management, asynchrone Videoverarbeitung und HLS (HTTP Live Streaming).

---

## ✨ Features

### 🔐 Sichere Authentifizierung  
Vollständiger Registrierungs- und Anmeldeprozess mit E-Mail-Bestätigung und sicherem, Cookie-basiertem JWT-Authentifizierungssystem (Access & Refresh Tokens).

### 🎞️ Asynchrone Videoverarbeitung  
Hochgeladene Videos werden automatisch im Hintergrund verarbeitet, ohne die API zu blockieren.

### 🚀 HLS Adaptive Bitrate Streaming  
Videos werden in verschiedene Auflösungen (1080p, 720p, 480p) konvertiert und als HLS-Streams (Playlist .m3u8 und Segmente .ts) bereitgestellt.

### 🖼️ Automatische Thumbnail-Erstellung  
Für jedes Video wird automatisch ein Vorschaubild generiert.

### ✅ Umfassende API  
Bietet Endpunkte für die Verwaltung und Bereitstellung von Videos und Streams.

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework  
- **Datenbank:** PostgreSQL  
- **Caching & Task Queue:** Redis  
- **Asynchrone Aufgaben:** django-rq  
- **Videoverarbeitung:** FFmpeg  
- **Containerisierung:** Docker (Tool zur einfachen Bereitstellung von Anwendungen), Docker Compose  
- **WSGI Server:** Gunicorn  

---

## 🚀 Getting Started

Es gibt zwei Wege, das Projekt aufzusetzen: mit Docker (empfohlen) oder manuell mit Python.

### Methode 1: Projekt mit Docker aufsetzen (Empfohlen)

Docker ist ein Tool zur einfachen Bereitstellung von Anwendungen, das alle notwendigen Programme (wie Python, PostgreSQL und Redis) automatisch für dich installiert und konfiguriert. Du musst nur Docker Desktop installieren.

#### 1. Voraussetzungen

- **Git:** Zum Klonen des Projekts.  
- **Docker Desktop:** Enthält Docker und Docker Compose. Lade es hier herunter: [Docker Desktop](https://www.docker.com/products/docker-desktop). Starte Docker Desktop nach der Installation.

#### 2. Projekt klonen

Öffne dein Terminal (oder die Kommandozeile auf Windows) und gib diese Befehle ein:  
```bash
git clone <REPO-URL>  # Klont das Projekt von der Quelle
cd <Projektordner>    # Wechselt in den Projektordner
```

#### 3. Die virtuelle Umgebung erstellen

Öffne das Projekt in deinem Code Editing Programm (zum Beispiel [Visual Studio Code](https://code.visualstudio.com/download)) und öffne ein neues Terminal. Erstelle eine virtuelle Umgebung (empfohlen, um Projekt-Abhängigkeiten sauber zu halten) und aktiviere sie:  
```bash

# Für Windows:
python -m venv env  # Erstellt eine virtuelle Umgebung
.\venv\Scripts\activate  # Aktiviert die virtuelle Umgebung

# Für macOS/Linux:
python3 -m venv env  # Erstellt eine virtuelle Umgebung
source venv/bin/activate  # Aktiviert die virtuelle Umgebung
```

#### 4. Die .env-Datei vorbereiten

Im Hauptordner des Projekts gibt es eine Datei namens `env.template`. Sie enthält die Standardeinstellungen für die Umgebungsvariablen. Erstelle eine Kopie davon und nenne sie `.env`.  
```bash
cp env.template .env  # Erstellt eine Kopie der Beispiel-Umgebungsdatei
```

Öffne die neue `.env`-Datei in einem Texteditor (z.B. Notepad, VS Code). Die Standardwerte sind für die lokale Entwicklung in der Regel in Ordnung, du musst sie also nicht unbedingt ändern. Sie sehen ungefähr so aus:  
```env
# Django
DEBUG=True
SECRET_KEY=dein-geheimer-key
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Django Superuser (wird automatisch beim Start erstellt)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword
```

> **Hinweis:** Für Docker Compose müssen `DB_HOST` und `REDIS_HOST` auf die jeweiligen Containernamen (`db` und `redis`) gesetzt werden, da die Dienste so miteinander kommunizieren. Diese sind in der `docker-compose.yml` definiert.

#### 5. Docker-Container starten

Jetzt starten wir alle Teile des Projekts auf einmal. Dieser Befehl baut die Images (so etwas wie Vorlagen für die Programme), startet die Services (Web-API, Datenbank, Redis) und führt alle notwendigen Einrichtungsschritte aus (z. B. Datenbankmigrationen).  
```bash
docker-compose up --build  # Baut und startet alle Container
```

Tipp: Wenn du die Container im Hintergrund laufen lassen möchtest, damit dein Terminal frei bleibt, verwende:  
```bash
docker-compose up --build -d  # Startet Container im Hintergrund (detached mode)
```

Nach ein paar Minuten ist die Anwendung unter [http://localhost:8000](http://localhost:8000) erreichbar. 🎉

> **Hinweis:** Auf macOS muss die Datei `entrypoint.sh` (oder das entsprechende Startskript) ausführbar gemacht werden, damit das Skript ausgeführt werden kann. Dies kannst du mit folgendem Befehl tun:  
> ```bash
> chmod +x backend.entrypoint.sh
> ```

---

### Methode 2: Manuelles Setup mit Python

Wenn du das Projekt ohne Docker direkt auf deinem Computer ausführen möchtest, folge dieser Anleitung.

#### 1. Voraussetzungen

- **Python 3.10+:** Stelle sicher, dass Python auf deinem System installiert ist. Du kannst es von der offiziellen Python-Website herunterladen: [python.org](https://www.python.org/).  
- **PostgreSQL:** Installiere und starte einen PostgreSQL-Datenbankserver. Anleitungen findest du auf der [PostgreSQL-Website](https://www.postgresql.org/).  
- **Redis:** Installiere und starte einen Redis-Server. Informationen dazu gibt es auf der [Redis-Website](https://redis.io/).  
- **FFmpeg:** Installiere FFmpeg, damit die Videoverarbeitung funktioniert. Offizielle Anleitungen findest du auf der [FFmpeg-Website](https://ffmpeg.org/).

#### 2. Projekt klonen und einrichten

Öffne dein Terminal und führe diese Befehle aus:  
```bash
git clone <REPO-URL>  # Klont das Projekt
cd <Projektordner>    # Wechselt in den Projektordner
```

Erstelle eine virtuelle Umgebung (empfohlen, um Projekt-Abhängigkeiten sauber zu halten) und aktiviere sie:  
```bash
python -m venv env  # Erstellt eine virtuelle Umgebung

# Für Windows:
.\env\Scripts\activate  # Aktiviert die virtuelle Umgebung

# Für macOS/Linux:
source env/bin/activate  # Aktiviert die virtuelle Umgebung
```

#### 3. Abhängigkeiten installieren

Installiere alle benötigten Python-Pakete aus der `requirements.txt`-Datei:  
```bash
pip install -r requirements.txt  # Installiert alle benötigten Pakete
```

#### 4. Die .env-Datei vorbereiten

Erstelle eine `.env`-Datei, ähnlich wie in der Docker-Anleitung beschrieben. Wichtig: Die Werte für `DB_HOST` und `REDIS_HOST` müssen hier `localhost` sein, da die Dienste direkt auf deinem lokalen Rechner laufen.  
```env
# .env-Datei für manuelles Setup
SECRET_KEY=dein-geheimer-key
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=localhost  # Hier "localhost" verwenden!
DB_PORT=5432
REDIS_HOST=localhost # Hier "localhost" verwenden!
REDIS_PORT=6379
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=dein@email.de
EMAIL_HOST_PASSWORD=dein-email-passwort
```

#### 5. Datenbank migrieren und Superuser anlegen

Führe die Datenbankmigrationen aus, um die Datenbankstruktur zu erstellen, und erstelle einen Admin-Benutzer für das Django-Admin-Interface:  
```bash
python manage.py migrate       # Erstellt die Datenbanktabellen
python manage.py createsuperuser  # Erstellt einen Admin-Benutzer
```

Folge den Anweisungen im Terminal, um Benutzername, E-Mail und Passwort für den Admin festzulegen.

#### 6. Server starten

Starte den Django-Entwicklungsserver und den RQ-Worker in zwei separaten Terminalfenstern:  
```bash
# Terminal 1: Django-Server starten
python manage.py runserver  # Startet den Entwicklungsserver

# Terminal 2: RQ-Worker starten (für die asynchronen Aufgaben wie Videokonvertierung)
python manage.py rqworker   # Startet den Task-Worker
```

Die Anwendung ist jetzt unter [http://localhost:8000](http://localhost:8000) erreichbar.

---

## 📄 API-Übersicht

Das Projekt stellt folgende Haupt-Endpunkte zur Verfügung:

| Methode | Pfad                                   | Beschreibung                          |
|---------|---------------------------------------|-------------------------------------|
| POST    | /api/register/                        | Registrierung                       |
| POST    | /api/login/                          | Login (JWT in Cookies)              |
| POST    | /api/logout/                         | Logout (Token-Blacklist, Cookies)  |
| POST    | /api/password_reset/                 | Passwort-Reset anfordern            |
| POST    | /api/password_confirm/<uid>/<token>/ | Neues Passwort setzen               |
| GET     | /api/video/                         | Liste aller Videos                  |
| GET     | /api/video/<id>/                    | Einzelnes Video                     |
| GET     | /api/video/<id>/<auflösung>/index.m3u8 | HLS Playlist für Video             |
| GET     | /api/video/<id>/<auflösung>/<segment>/ | HLS Segment                       |

---

## 🧪 Tests ausführen

Die gesamte Testsuite kann mit einem einzigen Befehl ausgeführt werden:

- **Mit Docker:**  
  ```bash
  docker compose exec web python manage.py test  # Führt alle Tests im Docker-Container aus
  ```

- **Manuell (ohne Docker):**  
  ```bash
  python manage.py test  # Führt alle Tests in der aktiven virtuellen Umgebung aus
  ```

---

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die LICENSE-Datei für weitere Details.
