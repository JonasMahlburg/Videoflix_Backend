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

---

## Projekt mit Docker aufsetzen

Falls du noch keine Berührungspunkte mit Docker hatest, folge dieser Schritt-für-Schritt-Anleitung:

### 1. **Docker & Docker Compose installieren**

- **Mac:**  
  Lade [Docker Desktop für Mac](https://www.docker.com/products/docker-desktop/) herunter und installiere es.
- **Windows:**  
  Lade [Docker Desktop für Windows](https://www.docker.com/products/docker-desktop/) herunter und installiere es.
- **Linux:**  
  Folge der [offiziellen Installationsanleitung](https://docs.docker.com/engine/install/).

Starte Docker Desktop nach der Installation.

### 2. **Projekt klonen**

```bash
git clone <REPO-URL>
cd Videoflix/Backend
```

### 3. **.env Datei anlegen**

Lege im Backend-Ordner eine Datei `.env` mit folgendem Inhalt an (passe die Werte an):

```
SECRET_KEY=dein-geheimer-key
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=dein-db-passwort
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=dein@email.de
EMAIL_HOST_PASSWORD=dein-email-passwort
```

**Hinweis:**  
Für Docker müssen `DB_HOST=db` und `REDIS_HOST=redis` gesetzt sein, da die Container so heißen!

### 4. **Docker-Container starten**

Im Projektordner (wo die `docker-compose.yml` liegt):

```bash
docker compose up --build
```

- Beim ersten Mal werden alle Images gebaut und die Abhängigkeiten installiert.
- Die Anwendung ist nach kurzer Zeit unter [http://localhost:8000](http://localhost:8000) erreichbar.

### 5. **Superuser anlegen**

Öffne ein neues Terminal und führe im laufenden Container folgenden Befehl aus:

```bash
docker compose exec web python manage.py createsuperuser
```

Folge den Anweisungen, um einen Admin-Account zu erstellen.

### 6. **Migrationen manuell ausführen (optional)**

Falls nötig, kannst du Migrationen auch manuell ausführen:

```bash
docker compose exec web python manage.py migrate
```

### 7. **RQ Worker läuft automatisch**

Der RQ Worker wird beim Starten des Containers automatisch mitgestartet.

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
docker compose exec web python manage.py test
```

---

## Hinweise

- Für die Videoverarbeitung muss FFmpeg installiert und im PATH verfügbar sein (im Docker-Image bereits enthalten).
- Die Medien-Dateien werden im Ordner `media/` gespeichert.
- Für produktiven Einsatz sollten `DEBUG=False` und sichere Einstellungen gewählt werden.

---

**Lizenz:** MIT  
**Autor:** Jonas Mahlburg