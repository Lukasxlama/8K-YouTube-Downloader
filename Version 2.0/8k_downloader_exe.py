"""
filename: 8k_downloader_exe.py
author: lukasxlama
version: 2.0 | exe
"""


from os import environ, pathsep, path, listdir, rename
from subprocess import call
from winreg import OpenKey, QueryValueEx, KEY_ALL_ACCESS, HKEY_CURRENT_USER, SetValueEx, REG_EXPAND_SZ, CloseKey

def add_ffmpeg_to_path(PATH: str) -> None:  # NOQA
    """
    Fügt FFMPEG zur Umgebungsvariable hinzu, um es für YT-DLP nutzbar zu machen.
    :param PATH: Pfad, der hinzugefügt wird. (ffmpeg\bin)
    :return: Gibt nichts zurück.
    """

    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    value, _ = QueryValueEx(key, 'Path')
    paths = value.split(pathsep)

    if PATH not in paths:
        paths.append(PATH)
        new_value = pathsep.join(paths)
        SetValueEx(key, 'Path', 0, REG_EXPAND_SZ, new_value)
        CloseKey(key)
        environ['PATH'] = new_value

    print("FFMPEG wurde zur Umgebungsvariable 'Path' hinzugefügt..")

def download_yt_dlp():
    """
    Installiert mit pip YT-DLP.
    :return: Gibt nichts zurück.
    """

    call(["pip", "install", "yt-dlp"])

def get_IDs(URL: str, PLAYLIST: bool = False) -> str:  # NOQA
    """
    Schneidet die YouTube-Video-ID aus dem Link.
    :param URL: YouTube-URL
    :param PLAYLIST: Bool-Variable, die angibt, ob die URL auf eine Playlist verweist. (Optional)
    :return: Liefert die Video-ID in Form eines Strings zurück.
    """

    if PLAYLIST:
        return URL.split("?list=")[1]
    elif "youtu.be" in URL:
        return URL.split("/")[3]
    elif "youtube.com/watch?v=" in URL:
        return URL.split("=")[1][:11]
    else:
        raise ValueError(f"Die URL ist ungültig! (URL = {URL})")

def get_flag(URL: str) -> str:  # NOQA
    """
    Überprüft, ob die URL auf eine Playlist oder ein Video verweist.
    :param URL: URL des Videos bzw. der Playlist.
    :return: Liefert eine String-Flag zurück.
    """

    if "?list=" in URL:
        return 'playlist'
    elif "?v=" in URL or "youtu.be" in URL:
        return 'file'
    else:
        raise ValueError(f"Aus der URL konnten keine Informationen gelesen werden! (URL = {URL}")

def download_mp4(URL: str, PATH: str) -> None:  # NOQA
    """
    Lädt YouTube-Videos im MP4 Format herunter.
    :param URL: URL des Videos bzw. der Playlist.
    :param PATH: Pfad, wo die Datei(en) gespeichert wird/werden.
    :return: Liefert nichts zurück.
    """

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
                 '--yes-playlist', get_IDs(URL, True)])

            print(f"\nDownload der Playlist abgeschlossen.. [MP4]")

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_01:
        print(f"Fehlermeldung: {Error_01}!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()

def download_mp3(URL: str, PATH: str) -> None:  # NOQA
    """
    Lädt YouTube-Videos im MP3 Format herunter.
    :param URL: URL des Videos bzw. der Playlist.
    :param PATH: Pfad, wo die Datei(en) gespeichert wird/werden.
    :return: Liefert nichts zurück.
    """

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
                 f"{PATH}/%(playlist_index)s_%(title)s.%(ext)s", '--yes-playlist', get_IDs(URL, True)])

            print(f"\nDownload der Playlist abgeschlossen.. [MP3]")

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_02:
        print(f"Fehlermeldung: {Error_02}!")
        input("Drücke ENTER, um das Programm zu beenden..")
        exit()


if __name__ == "__main__":
    run=0

    while True:
        run += 1

        try:
            if run == 1:
                print("~~ 8k YouTube Downloader ~~")
                print(fr"--> {path.dirname(path.abspath(__file__))}\ffmpeg\bin")
                install_dependencies = input("Abhängigkeiten installieren? [Y/N]\n-> ").lower()

            else:
                install_dependencies = "n"

            if install_dependencies == "y":
                download_yt_dlp()
                add_ffmpeg_to_path(fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin")

            elif install_dependencies == "n":
                URL = input("--URL: ")
                FORM = input("--FORMAT: ")
                PATH = input("--OUTPUT_PATH: ")

                if "MP3" in FORM and "MP4" in FORM:
                    download_mp3(URL, fr"{PATH}\MP3")
                    download_mp4(URL, fr"{PATH}\MP4")
                elif "MP3" in FORM:
                    download_mp3(URL, PATH)
                elif "MP4" in FORM:
                    download_mp4(URL, PATH)
                else:
                    raise ValueError(f"FORM = {FORM}")

            else:
                raise ValueError("Invalid Option!")

        except (KeyboardInterrupt, EOFError) as Error_03:
            print(f"Das Programm wurde unterbrochen!")
            exit()

        except Exception as Error_04:
            print(f"Fehlermeldung: {Error_04}!")
            continue

        except BaseException as Error_05:
            print(f"Kritische Fehlermeldung: {Error_05}!")
            continue

input("Drücke ENTER, um das Programm zu beenden..")
exit()