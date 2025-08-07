# Videoflix Backend

Das ist das Backend der Videoflix-Plattform, entwickelt mit Django, Django REST Framework, PostgreSQL und Redis (RQ).  
Es stellt eine API für User-Registrierung, Authentifizierung, Video-Upload, Video-Konvertierung (FFmpeg), HLS-Streaming und mehr bereit.

---

## Features

- Benutzerregistrierung mit E-Mail-Bestätigung
- JWT-Authentifizierung (Token in HttpOnly-Cookies)
- Passwort-Reset per E-Mail
- Video-Upload und automatische Konvertierung in 480p, 720p, 1080p (FFmpeg)
- Automatische Thumbnail-Erstellung
- HLS-Streaming (M3U8/TS)
- Admin-Interface
- RQ-Worker für asynchrone Aufgaben (Video-Konvertierung, Thumbnail, HLS)
- CORS-Unterstützung für Frontend-Anbindung

---

## Setup

### Voraussetzungen

- Python 3.10+
- PostgreSQL
- Redis (für RQ)
- FFmpeg (für Videoverarbeitung)
- pipenv oder pip

### Installation

1. **Repository klonen**
   ```bash
   git clone <REPO-URL>
   cd Videoflix/Backend
   ```

2. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

3. **.env Datei anlegen**  
   Beispiel:
   ```
   SECRET_KEY=dein-geheimer-key
   DB_NAME=videoflix_db
   DB_USER=videoflix_user
   DB_PASSWORD=dein-db-passwort
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_HOST=localhost
   REDIS_PORT=6379
   EMAIL_HOST=smtp.example.com
   EMAIL_HOST_USER=dein@email.de
   EMAIL_HOST_PASSWORD=dein-email-passwort
   ```

4. **Migrationen anwenden**
   ```bash
   python manage.py migrate
   ```

5. **Superuser anlegen**
   ```bash
   python manage.py createsuperuser
   ```

6. **RQ Worker starten**
   ```bash
   python manage.py rqworker default
   ```

7. **Server starten**
   ```bash
   python manage.py runserver
   ```

---

## API-Endpunkte (Auszug)

| Methode | Pfad                                 | Beschreibung                       |
|---------|--------------------------------------|------------------------------------|
| POST    | `/api/register/`                     | Registrierung                      |
| POST    | `/api/login/`                        | Login (JWT in Cookies)             |
| POST    | `/api/logout/`                       | Logout (Token-Blacklist, Cookies)  |
| POST    | `/api/password_reset/`               | Passwort-Reset anfordern           |
| POST    | `/api/password_confirm/<uid>/<token>/` | Neues Passwort setzen              |
| GET     | `/api/video/`                        | Liste aller Videos                 |
| GET     | `/api/video/<id>/`                   | Einzelnes Video                    |
| GET     | `/api/video/<id>/<auflösung>/index.m3u8` | HLS Playlist für Video             |
| GET     | `/api/video/<id>/<auflösung>/<segment>/` | HLS Segment                        |

---

## Tests

Alle Tests können mit folgendem Befehl ausgeführt werden:

```bash
python manage.py test
```

---

## Hinweise

- Für die Videoverarbeitung muss FFmpeg installiert und im PATH verfügbar sein.
- Die Medien-Dateien werden im Ordner `media/` gespeichert.
- Für produktiven Einsatz sollten `DEBUG=False` und sichere Einstellungen gewählt werden.

---

**Lizenz:** MIT  
**Autor:** Jonas Mahlburg