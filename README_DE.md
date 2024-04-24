# 8K YouTube Downloader - Version 7.0

## Über das Projekt

Der 8K YouTube Downloader ist ein praktisches Tool zum Herunterladen von YouTube-Videos in verschiedenen Auflösungen, einschließlich bis zu 8K. Diese Version bietet eine komplette Überarbeitung des Codes und das Hinzufügen neuer Features, wie z.B. die automatische Thumbnail-Einbettung in MP3- und MP4-Dateien.

## Features

- Herunterladen von Videos in bis zu 8K Auflösung
- Playlist-Download-Unterstützung
- Unterstützung von MP3- und MP4-Downloads
- Moderne Benutzeroberfläche mit CustomTkinter (CTk)
- Erweiterte Fehlerbehandlung und Logging

## Anforderungen

- Python 3.8 oder höher
- FFMPEG
- `yt_dlp`: Eine Bibliothek zum Herunterladen von Videos und Playlists von YouTube.
- `Pillow`: Eine Bibliothek zur Bearbeitung von Bildern. Wird als Nachfolger von PIL (Python Imaging Library) verwendet.
- `customtkinter`: Eine erweiterte Version von Tkinter, die verbesserte und modernere UI-Komponenten bietet.
- `CTkMessagebox`: Ein erweitertes MessageBox-Widget, das CustomTkinter verwendet.

Zusätzlich werden mehrere Python-Standardbibliotheken verwendet, die mit der Python-Installation bereitgestellt werden und keine gesonderte Installation erfordern:

- `winreg` (nur auf Windows-Systemen verfügbar)
- `os`
- `concurrent.futures`
- `subprocess`
- `re`
- `logging`
- `time`
- `tkinter`

## Installation der Abhängigkeiten

Um die erforderlichen Python-Pakete zu installieren, führen Sie den folgenden Befehl aus:

```bash
pip install yt_dlp Pillow customtkinter CTkMessagebox
```

## Installation - FFMPEG
Für die Installation von `FFMPEG` folgen Sie bitte diesen Schritten:
1. Laden Sie die `FFMPEG`-Binärdateien von der offiziellen Webseite [ffmpeg.org](https://ffmpeg.org/download.html) herunter, oder nutzen Sie [diesen Shortcut]((https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z))
2. Extrahieren Sie das heruntergeladene Archiv in den Ordner, in dem sich Ihr Programm befindet. Die Struktur sollte wie folgt aussehen:

    ```
    8K_YouTube_Downloader/
    ├── ffmpeg/
    │   └── bin/
    │       ├── ffmpeg.exe
    │       └── ffprobe.exe
    │       ...
    │
    ├── __main__.py
    ├── Dependencies.py
    ├── DownloadVideo.py
    ├── ExtractVideoID.py
    ├── LoggerConfig.py
    ├── MessageBoxes.py
    │   ...
    ```

    Der Pfad fr`{path.dirname(path.abspath(__file__))}\ffmpeg\bin` ist entscheidend für die Funktionsfähigkeit des Programms. Wenn FFMPEG nicht in diesem Verzeichnis gefunden wird, wird das Programm mit einer log.critical Fehlermeldung beendet.

3. Stellen Sie sicher, dass Sie die Pfadangaben in der `DownloadVideo.py` entsprechend anpassen, falls Sie eine andere Struktur verwenden möchten. Das Programm erwartet, dass die `ffmpeg.exe` und `ffprobe.exe` Dateien im oben angegebenen `ffmpeg\bin` Verzeichnis liegen.

## Offizielle Webseiten und Dokumentation
- `yt_dlp`: [GitHub Repository von yt-dlp](https://github.com/yt-dlp/yt-dlp)
- `CustomTkinter`: [GitHub Repository von CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- `CTkMessageBox`: [GitHub Repository von CTkMessageBox](https://github.com/Akascape/CTkMessagebox)
