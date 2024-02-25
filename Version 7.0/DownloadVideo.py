##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: DownloadVideo.py    #
# Version: 7.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggerConfig import getLoggerConfig
    import logging as log

    ## Eigene Module ##
    from ExtractVideoID import *
    from Dependencies import *

    ## YouTube-DLP, Threads, Terminal, Bild, RegEx, Pfad- und Dateiverwaltung #
    from concurrent.futures import ThreadPoolExecutor
    from subprocess import run, CalledProcessError
    from os import path, listdir, rename, remove
    from yt_dlp import YoutubeDL
    from PIL import Image
    from re import sub
    import sys
except ImportError as e:
    print(f"[DownloadVideo.py] Fehler beim Import: {e}")
    sys.exit(-810)


### Logger starten ###
getLoggerConfig()


### Klassen ###
class VideoDownloadError(Exception):
    """
    Eine Exception-Klasse, die bei Fehlern beim Download geworfen wird.
    """

    def __init__(self, message="Fehler beim Download!"):
        self.message = message
        super().__init__(self.message)


### Globals ###
downloadProgress: float = 0


### Funktionen ###
def convertToPNG(FILE: str) -> str:
    """
    Konvertiert mit PIL das Thumbnail in .png
    :param FILE: Thumbnai-Datei als .webp
    :return: Den neuen Dateinamen
    """

    try:
        output = path.splitext(FILE)[0] + ".png"
        with Image.open(FILE) as f:
            f.save(output, "PNG")

        remove(FILE)
        log.info(f"[DownloadVideo.py] Erfolgreich die Erweiterung von {FILE} zu .png geändert.")
        return output
    except Exception as e:
        log.error(f"[DownloadVideo.py] Fehler beim Konvertieren von {FILE}: {e}")


def addThumbnailToMedia(FILE: str, THUMBNAIL: str) -> None:
    """
    Fügt ein Thumbnail zu einer Mediendatei hinzu.

    :param FILE: Pfad zur Mediendatei (MP3 oder MP4).
    :param THUMBNAIL: Pfad zur Thumbnail-Datei im .webp-Format.
    """

    if not path.exists(FILE) or not path.exists(THUMBNAIL):
        log.error(f"[DownloadVideo.py] Datei oder Thumbnail existiert nicht: {FILE}, {THUMBNAIL}")
        return

    output_file = FILE.rsplit('.', 1)[0] + "_thumb." + FILE.rsplit('.', 1)[1]
    output_thumb = convertToPNG(THUMBNAIL)

    if FILE.endswith('.mp4'):
        cmd = [
                'ffmpeg', '-i', FILE, '-i', output_thumb,
                '-map', '0', '-map', '1', '-c', 'copy', '-disposition:v:1', 'attached_pic',
                output_file
              ]

    elif FILE.endswith('.mp3'):
        cmd = [
                'ffmpeg', '-i', FILE, '-i', output_thumb,
                '-map', '0', '-map', '1', '-c', 'copy', '-id3v2_version', '3',
                '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"',
                output_file
              ]

    else:
        log.error(f"[DownloadVideo.py] Nicht unterstütztes Dateiformat: {FILE}")
        return

    try:
        run(cmd, check=True)
        remove(output_thumb)
        remove(FILE)
        rename(output_file, FILE)
        log.info(f"[DownloadVideo.py] Thumbnail erfolgreich zu {FILE} hinzugefügt")
    except CalledProcessError as e:
        log.error(f"[DownloadVideo.py] Fehler beim Hinzufügen des Thumbnails zu {FILE}", exc_info=e)
    except Exception as e:
        log.error(f"[DownloadVideo.py] Unbekannter Fehler beim Hinzufügen des Thumbnails zu {FILE}", exc_info=e)


def downloadProcess(DIR: str) -> None:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for file in listdir(DIR):
            full_path = path.join(DIR, file)
            if '.8kdownload' in file and (file.endswith(".mp4") or file.endswith(".mp3")):
                thumbnail_file = path.splitext(full_path)[0] + ".webp"
                future = executor.submit(addThumbnailToMedia, full_path, thumbnail_file)
                futures.append(future)

        for future in futures:
            future.result()

        for file in listdir(DIR):
            full_path = path.join(DIR, file)
            if '.8kdownload' in file:
                path_old = full_path
                path_new = path_old.replace(".8kdownload", "")
                rename(path_old, path_new)
                log.info(f"Datei umbenannt: {path_new}")

def progressHook(STATUS: dict) -> None:
    if STATUS['status'] == 'downloading':
        progress_percent = float(sub(r".*?(\d+\.\d+%).*", r"\1", STATUS['_percent_str']).replace("%", ""))

    elif STATUS['status'] == 'finished':
        progress_percent = 100.0

    global downloadProgress
    downloadProgress = progress_percent

def downloadVideo(URL: str, PATH: str, FLAG: str, FORMAT: str = 'MP4', QUAL: tuple = (320, (320, 4320))) -> bool:
    """
    Lädt ein Video oder eine Playlist von YouTube herunter und speichert die Datei[en] lokal ab.

    :param URL: Die YouTube-URL des Videos oder der Playlist, welche[s] heruntergeladen werden soll.
    :param PATH: Der Pfad zum Verzeichnis, in dem die heruntergeladene Datei gespeichert werden soll.
    :param FLAG: Eine Flag, die angibt, ob das Video oder die Playlist heruntergeladen werden soll.
    :param FORMAT: Das gewünschte Format des Downloads ('mp4' für Video, 'mp3' für Audio).
    :param QUAL: Legt die bevorzugte Qualität des Videos fest (Audio: 320kbps, Video: (Audio: 320kbps, Video: 4320p))
    :return: True für Erfolg, False für Misserfolg
    """

    try:
        ID, SWITCH = getVideoID(URL, FLAG)
        FFMPEG(fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin")

        ydl_opts = {
                    'outtmpl': path.join(PATH, '%(title)s.8kdownload.%(ext)s'),
                    'progress_hooks': [progressHook],
                    'writethumbnail': True,
                    'sleep_interval': 10,
                    'max_sleep_interval': 30,
                    'quiet': True,
                    'merge_output_format': FORMAT.lower(),
                    'ffmpeg_location': fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin"
                   }

        if FORMAT == 'MP4':
            ydl_opts.update({
                            'format': f'bestvideo[height<={QUAL[1][1]}]+bestaudio[abr<={QUAL[1][0]}][ext=m4a]/best[height<={QUAL[1][1]}]',
                            })

        elif FORMAT == 'MP3':
            ydl_opts.update({
                            'format': 'bestaudio[ext=m4a]/best',
                            'extract_audio': True,
                            'audio_format': 'mp3',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': f'{QUAL[0]}',
                                }],
                            })

        else:
            raise VideoDownloadError(f"[DownloadVideo.py] Ungültiges Format: {FORMAT}")

        if SWITCH in ["VIDEO", "SHORTS"]:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={ID}"])

        elif SWITCH == "PLAYLIST":
            ydl_opts['yes_playlist'] = True
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/playlist?list={ID}"])

        else:
            raise VideoDownloadError(f"[DownloadVideo.py] Die angegebene Flag ist ungültig: {SWITCH}")

        downloadProcess(PATH)

        return True

    except VideoDownloadError as e:
        log.error(f"[DownloadVideo.py] Fehler beim Herunterladen der {FORMAT}-Datei", exc_info=e)
        return False

    except BaseException as e:
        log.critical("[DownloadVideo.py] CRITICAL-ERROR beim Herunterladen", exc_info=e)
        sys.exit(-810)

if __name__ == '__main__':
    from time import time
    start_time = time()
    downloadVideo("https://www.youtube.com/watch?v=L9DK-DRg85w", "D:\Medien\Desktop", "VIDEO", "MP4")
    end_time = time()
    print(f"Das Herunterladen des Videos (4K@60 | 122 Sekunden) hat {end_time - start_time} Sekunden benötigt.")