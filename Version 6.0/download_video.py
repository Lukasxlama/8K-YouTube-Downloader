##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: download_video.py   #
# Version: 6.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    from get_video_informations import *
    from messageboxes import show_error
    from os import path, listdir, rename, remove
    from dependencies import *
    from yt_dlp import *
except ImportError:
    exit()


### Funktionen ###
def download_mp4(URL: str, PATH: str, BUTTON: str = None, QUAL: int = 4320) -> int:
    """
    Lädt ein Video oder eine Playlist im MP4 Format von YouTube herunter und speichert die Datei[en] lokal ab.

    :param URL: Die YouTube-URL des Videos oder der Playlist, das/die heruntergeladen werden soll.
    :param PATH: Der Pfad zum Verzeichnis, in dem die heruntergeladene Datei gespeichert werden soll.
    :param BUTTON: Eine Flag, die bei einer "&list=" URL angibt, ob das Video oder die Playlist heruntergeladen werden soll.
    :param QUAL: Legt die bevorzugte Qualität des Videos fest. Standart: 4320p (8K)
    :raises Exception: Bei Auftreten einer Exception wird -1 zurückgeliefert.
    :return: Eine Ganzzahl, die den Erfolg des Downloads darstellt. 1 für Erfolg, -1 für einen Fehler.
    """

    try:
        ID, FLAG = get_url_informations(URL, BUTTON)
        FFMPEG(fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin")

        ydl_opts = {'format': f'bestvideo[height<={QUAL}]+bestaudio[ext=m4a]/best[height<={QUAL}]',
                    'outtmpl': path.join(PATH, '%(title)s.%(ext)s'),
                    'progress_hooks': [],
                    'writethumbnail': False,
                    'sleep_interval': 5,
                    'max_sleep_interval': 20,
                    'verbose': True,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin"}

        if FLAG == 'VIDEO':
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={ID}"])

        elif FLAG == "PLAYLIST":
            ydl_opts['yes_playlist'] = True

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/playlist?list={ID}"])

        else:
            return -1

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

        return 1

    except Exception as Error_01:
        print(Error_01)
        return -1

def download_mp3(URL: str, PATH: str, BUTTON: str) -> int:
    try:
        ID, FLAG = get_url_informations(URL, BUTTON)
        FFMPEG(fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin")

        ydl_opts = {'format': 'bestaudio[ext=m4a]/best',
                    'outtmpl': path.join(PATH, '%(title)s.%(ext)s'),
                    'progress_hooks': [],
                    'extract_audio': True,
                    'audio_format': 'mp3',
                    'sleep_interval': 5,
                    'max_sleep_interval': 20,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'verbose': True,
                    'ffmpeg_location': fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin"}

        if FLAG == 'VIDEO':
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={ID}"])

        elif FLAG == "PLAYLIST":
            ydl_opts['yes_playlist'] = True

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/playlist?list={ID}"])

        else:
            return -1

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

        return 1

    except Exception as Error_02:
        print(Error_02)
        return -1
