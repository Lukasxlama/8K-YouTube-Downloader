from os import listdir, rename, path
from subprocess import call
from argparse import ArgumentParser


def get_IDs(URL: str, PLAYLIST: bool = False):
    if PLAYLIST and "playlist?list=":
        return URL.split("list=")[1]
    elif "youtu.be" in URL:
        return URL.split("/")[3]
    elif "youtube.com/watch?v=" in URL:
        return URL.split("=")[1][:11]
    else:
        raise ValueError(f"Die URL ist ungültig! (URL = {URL})")

def get_flag(URL: str):
    if "?list=" in URL:
        return 'playlist'
    elif "?v=" in URL or "youtu.be" in URL:
        return 'file'
    else:
        raise ValueError(f"Aus der URL konnten keine Informationen gelesen werden! (URL = {URL}")

def download_mp4(URL: str, PATH: str):  # NOQA
    try:

        FLAG = get_flag(URL)

        if FLAG == 'file':
            call(
                ['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '-o',
                 f"{PATH}/%(title)s.%(ext)s", '--merge-output-format', 'mp4', get_IDs(URL)])

            print(f"\nDownload der Datei abgeschlossen.. [MP4]")

        if FLAG == "playlist":
            call(
                ['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '-o',
                 f"{PATH}/%(playlist_index)s_%(title)s.%(ext)s", '--merge-output-format', 'mp4',
                 '--yes-playlist', get_IDs(URL, PLAYLIST=True)])

            print(f"\nDownload der Playlist abgeschlossen.. [MP4]")

        # Präfixe entfernen
        for file in listdir(PATH):
            rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_01:
        print(f"Fehlermeldung: {Error_01}!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()

def download_mp3(URL: str, PATH: str):  # NOQA
    try:

        FLAG = get_flag(URL)

        if FLAG == 'file':
            call(
                ['yt-dlp', '-x', '--audio-format', 'mp3', '-o',
                 f"{PATH}/%(title)s.%(ext)s", get_IDs(URL)])

            print(f"\nDownload der Datei abgeschlossen.. [MP3]")

        if FLAG == "playlist":
            call(
                ['yt-dlp', '-x', '--audio-format', 'mp3', '-o',
                 f"{PATH}/%(playlist_index)s_%(title)s.%(ext)s", '--yes-playlist', get_IDs(URL, PLAYLIST=True)])

            print(f"\nDownload der Playlist abgeschlossen.. [MP3]")

        # Präfixe entfernen
        for file in listdir(PATH):
            rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_02:
        print(f"Fehlermeldung: {Error_02}!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()


if __name__ == "__main__":
    try:

        PARSER = ArgumentParser(description="YouTube Video Downloader")

        PARSER.add_argument("--URL", required=True, help="Die URL des YouTube-Videos oder der Playlist")
        PARSER.add_argument("--FORM", nargs="+", required=True, choices=["MP3", "MP4"], help="Die Formate zum Herunterladen")
        PARSER.add_argument("--OUTPUT_PATH", required=True, help="Der Pfad, wo die Dateien gespeichert werden.")

        ARGS = PARSER.parse_args()
        PATH = ARGS.OUTPUT_PATH

        if "MP3" in ARGS.FORM and "MP4" in ARGS.FORM:
            download_mp3(ARGS.URL, fr"{PATH}\MP3")
            download_mp4(ARGS.URL, fr"{PATH}\MP4")
        elif "MP3" in ARGS.FORM:
            download_mp3(ARGS.URL, PATH)
        elif "MP4" in ARGS.FORM:
            download_mp4(ARGS.URL, PATH)

    except Exception as Error_03:
        print(f"Fehlermeldung: {Error_03}!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()

    except KeyboardInterrupt as Error_04:
        print(f"Das Programm wurde unerwartet unterbrochen!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()