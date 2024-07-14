# 8K Video Downloader - Version 8.0

## Über das Projekt

Der 8K Video Downloader ist ein leistungsfähiges Tool zum Herunterladen von Video- und Audiodateien von verschiedenen Plattformen in unterschiedlichen Auflösungen, einschließlich bis zu 8K. Diese Version bietet eine komplette Überarbeitung des Codes und das Hinzufügen neuer Features. Beachte, dass dieses Programm derzeit nur unter Windows funktioniert.

## Features

- **Unterstützte Plattformen**: YouTube, Twitch, SoundCloud & Podcast.de
- **Auflösungen**: Herunterladen von Videos in bis zu 8K Auflösung
- **Thumbnails**: Herunterladen und Hinzufügen von Thumbnails
- **Untertitel**: Herunterladen und Hinzufügen von Untertiteln
- **Formate**: Unterstützung von MP3- und MP4-Downloads
- **Playlist-Downloads**: Unterstützung von Playlist-Downloads
- **Benutzeroberfläche**: Moderne GUI mit CustomTkinter
- **Erweiterte Optionen**: Über die Tastenkombination `STRG + O` zugänglich
- **Mehrere Downloads**: Beliebig viele Downloads über JSON-Datei

## Anforderungen

- `Python 3.8 oder höher` (getestet mit Python 3.12)
- `FFmpeg`
- `yt_dlp`
- `Pillow`
- `customtkinter`
- `CTkMessagebox`
- `beautifulsoup4`
- `requests`
- `vlc`

Zusätzlich werden mehrere Python-Standardbibliotheken verwendet, die keine gesonderte Installation erfordern:

- `winreg`
- `os`
- `subprocess`
- `re`
- `logging`
- `time`
- `tkinter`
- `sys`
- `typing`
- `datetime`
- `asyncio`
- `collections`
- `json`

## Einrichten der Umgebung

1. **Python-Version überprüfen**:
    ```bash
    python --version
    ```
    Falls die Version nicht `Python 3.8` oder höher ist, lade die neuste Version von Python [hier](https://www.python.org/downloads/) herunter und installiere sie. Stelle sicher, dass Python zum PATH hinzugefügt wird.

2. **Erforderliche Pakete installieren**:
    ```bash
    pip install yt_dlp Pillow customtkinter CTkMessagebox beautifulsoup4 requests python-vlc
    ```

3. **Verzeichnis von GitHub herunterladen**:
    Klicke auf [diesen Link](https://download-directory.github.io/?url=https://github.com/Lukasxlama/8K-YouTube-Downloader/tree/main/Version%208.0), um das Verzeichnis herunterzuladen und entpacke es in einen beliebigen Ordner. 

4. **FFmpeg installieren**:
    Gehe zu folgendem [Abschnitt](#installation---ffmpeg) für detaillierte Anweisungen zur Installation von FFmpeg.

5. **VLC Media Player installieren**:
    Lade den VLC Media Player von der offiziellen [VLC Webseite](https://www.videolan.org/vlc/index.html) herunter und installiere ihn.

6. <a id="schritt-6"></a> **Programm starten**:
    Navigiere zu dem Verzeichnis, in dem sich die `__main__.py`-Datei befindet, und führe folgenden Befehl aus:
    ```bash
    python .\__main__.py
    ```
    Wenn alles klappt, kannst du dir noch die [unterstützten Formate](#unterstützte-formate) ansehen.
    Falls keine GUI erscheint, überprüfe die Logs im Verzeichnis `\logs` auf Fehlermeldungen.

## Installation - FFmpeg

1. **FFmpeg-Binärdateien herunterladen**:
    Lade die `FFmpeg`-Binärdateien von der offiziellen Webseite [ffmpeg.org](https://ffmpeg.org/download.html) herunter oder nutze [diesen Shortcut](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z).

2. **Verzeichnisstruktur erstellen**:
    Extrahiere das heruntergeladene Archiv in das Programmverzeichnis. Die Struktur sollte wie folgt aussehen:
    ```
    8K_Video_Downloader/
    ├── ffmpeg/
    │   └── bin/
    │       ├── ffmpeg.exe
    │       └── ffprobe.exe
    │       ...
    ├── logs/
    │   └── ...
    ├── media/
    │   └── ...
    ├── themes/
    │   └── ...
    ├── __main__.py
    ├── DependenciesManager.py
    ├── DownloadManager.py
    ├── downloads.json
    ├── GUIManager.py
    ├── JSONManager.py
    ├── LinkManager.py
    ├── LoggingManager.py
    ├── MessageBoxManager.py
    ├── OutputStreamHandler.py
    ├── PostprocessorManager.py
    ```

Nun kannst du mit [Schritt 6](#schritt-6) fortfahren.

## Unterstützte Formate

| Platform       | Type                  | MP3  | MP4  | Subtitles | Thumbnail |
|----------------|-----------------------|------|------|-----------|-----------|
| **YouTube**    | Video                 | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Playlist              | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Shorts                | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Shorts Shortlink      | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Video Shortlink       | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | User                  | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Channel               | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Embedded              | ✅   | ✅   | ✅        | ✅        |
| **Twitch**     | VOD                   | ✅   | ✅   | ❌        | ✅        |
| **Twitch**     | Clip                  | ✅   | ✅   | ❌        | ✅        |
| **SoundCloud** | Track                 | ✅   | ❌   | ❌        | ✅        |
| **SoundCloud** | Playlist              | ✅   | ❌   | ❌        | ✅        |
| **Podcast.de** | Episode               | ✅   | ❌   | ❌        | ✅        |
| **Podcast.de** | Podcast               | ✅   | ❌   | ❌        | ✅        |

## Offizielle Webseiten und Dokumentation

Hier sind die Links zu den verwendeten Tools:

- `FFmpeg`: [Website](https://ffmpeg.org/)
- `yt_dlp`: [GitHub Repository](https://github.com/yt-dlp/yt-dlp)
- `CustomTkinter`: [GitHub Repository](https://github.com/TomSchimansky/CustomTkinter)
- `CTkMessageBox`: [GitHub Repository](https://github.com/Akascape/CTkMessagebox)
- `BeautifulSoup4`: [GitHub Repository](https://github.com/wention/BeautifulSoup4)
- `Pillow`: [GitHub Repository](https://github.com/python-pillow/Pillow)
- `requests`: [GitHub Repository](https://github.com/psf/requests)
- `vlc`: [GitHub Repository](https://github.com/oaubert/python-vlc/tree/master)
