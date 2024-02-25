########################################
# Projekt: 8K YouTube Downloader       #
# Dateiname: ExtractVideoID.py         #
# Version: 7.0                         #
# Autor: lukasxlama                    #
########################################


### Imports ###
try:
    ## Logging ##
    from LoggerConfig import getLoggerConfig
    import logging as log

    ## Regex & Benchmark ##
    from re import search
    from time import time
    import sys
except ImportError as e:
    print(f"[ExtractVideoID.py] Fehler beim Import: {e}")
    sys.exit(-810)


### Logger starten ###
getLoggerConfig()


### Klassen ###
class VideoIDExtractionError(Exception):
    """
    Eine Exception-Klasse, die bei Fehlern bei der Extraktion der Video-ID geworfen wird.
    """

    def __init__(self, message="Fehler beim Extrahieren der Video-ID!"):
        self.message = message
        super().__init__(self.message)


### Funktionen ###
def getVideoID(URL: str, FLAG: str = None) -> tuple[str, str]:
    """
    Extrahiert die Video-ID aus einer YouTube-URL mit regulären Ausdrücken.

    :param URL: Die YouTube-URL, aus der die Informationen extrahiert werden sollen.
    :param FLAG: Eine Flag, die angibt, ob nach einer Playlist- oder einer Video-ID gesucht werden soll.
                 Mögliche Werte sind "PLAYLIST" und "VIDEO". Standardmäßig ist sie None.
    :return: Ein Tupel aus zwei Zeichenketten (Video-/Playlist-ID und Typ) oder False bei einem Fehler.
    """

    try:
        video_pattern = r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})"
        playlist_pattern = r"list=([a-zA-Z0-9_-]{34})"

        video_match = search(video_pattern, URL)
        playlist_match = search(playlist_pattern, URL)

        if video_match and playlist_match:
            if FLAG == "PLAYLIST":
                return playlist_match.group(1), "PLAYLIST"
            elif FLAG == "VIDEO" or not FLAG:
                return video_match.group(1), "VIDEO"
        elif video_match:
            if "shorts" in URL:
                return video_match.group(1), "SHORTS"
            else:
                return video_match.group(1), "VIDEO"
        elif playlist_match:
            return playlist_match.group(1), "PLAYLIST"
        else:
            raise VideoIDExtractionError

    except VideoIDExtractionError as e:
        log.error(f"[ExtractVideoID.py] Die Video-ID konnte nicht extrahiert werden: {URL}", exc_info=e)
        return False
    except BaseException as e:
        log.critical("[ExtractVideoID.py] CRITICAL-ERROR", exc_info=e)
        sys.exit(-810)

def benchmark(url_list: list, flag_list: list) -> None:
    """
    Führt eine Benchmark-Analyse für eine Liste von URLs durch und gibt die Video-IDs und Typen aus.

    :param url_list: Eine Liste von YouTube-URLs, aus denen die Video-IDs extrahiert werden sollen.
    :param flag_list: Eine Liste von Flags, die angibt, ob nach Playlist- oder Video-IDs gesucht werden soll.
                      Die Reihenfolge der Flags sollte der Reihenfolge der URLs entsprechen.
                      Mögliche Werte für jedes Flag sind "VIDEO", "PLAYLIST" oder None (Standard).
    :return: None
    """

    start = time()
    for url in url_list:
        for flag in flag_list:
            try:
                video_id, video_type = getVideoID(url, flag)
                print(f"URL: {url}, Flag: {flag}\nVideo ID: {video_id}, Type: {video_type}\n")
            except VideoIDExtractionError as e:
                log.error(f"[ExtractVideoID.py->benchmark] Spezifischer Fehler bei der Verarbeitung von URL: {url} mit Flag: {flag}", exc_info=e)
            except BaseException as e:
                log.critical("[ExtractVideoID.py->benchmark()] CRITICAL-ERROR", exc_info=e)
                sys.exit(-810)

    end = time()
    print(f"Benchmark abgeschlossen in: {end - start} Sekunden")

if __name__ == "__main__":
    urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI",
            "https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI",
            "https://www.youtube.com/shorts/iAC7e0ZtuC8"
           ]

    flags = [
             "VIDEO",
             "PLAYLIST"
            ]

    benchmark(urls, flags)