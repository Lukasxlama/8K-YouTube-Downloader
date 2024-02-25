########################################
# Projekt: 8K YouTube Downloader       #
# Dateiname: get_video_informations.py #
# Version: 6.0                         #
# Autor: lukasxlama                    #
########################################


### Funktionen ###
def get_url_informations(URL: str, FLAG: str = None) -> tuple[str, str]:
    """
    Extrahiert Informationen aus einer YouTube-URL.

    :param URL: Die YouTube-URL, aus der die Informationen extrahiert werden sollen.
    :param FLAG: Eine Flag, die angibt, ob nach einer Playlist- oder einer Video-ID gesucht werden soll. Wird nur bei "&list=" benötigt.
                 Mögliche Werte sind "PLAYLIST" und "VIDEO". Standardmäßig ist sie None.
    :return: Ein Tupel aus zwei Zeichenketten (Video-/Playlist-ID und Typ) oder (URL_ERROR, URL_ERROR).
    :raises IndexError: Wird ausgelöst, wenn die URL nicht das erwartete Format hat und die Informationen nicht extrahiert werden können.
    """

    try:
        if "https://youtu.be/" in URL and \
                len(URL.split("/")[3][:11]) == 11:
            return URL.split("/")[3][:11], "VIDEO"

        elif "&list=" in URL and \
                len(URL.split("=")[2][:34]) == 34 and \
                len(URL.split("=")[1][:11]) == 11:

            if FLAG == "PLAYLIST":
                return URL.split("=")[2][:34], "PLAYLIST"
            elif FLAG == "VIDEO":
                return URL.split("=")[1][:11], "VIDEO"
            else:
                return "URL_ERROR"

        elif "https://www.youtube.com/watch?v=" in URL and \
                len(URL.split("=")[1][:11]) == 11:
            return URL.split("=")[1][:11], "VIDEO"

        elif "https://www.youtube.com/playlist?list=" in URL and \
                len(URL.split("=")[1][:34]) == 34:
            return URL.split("=")[1][:34], "PLAYLIST"

        elif "https://www.youtube.com/shorts/" in URL and \
                len(URL.split("/")[4][:11]) == 11:
            return URL.split("/")[4][:11], "VIDEO"

        else:
            return "URL_ERROR"

    except IndexError:
        return "URL_ERROR"