##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: MessageBoxes.py     #
# Version: 7.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggerConfig import getLoggerConfig
    import logging as log

    ## Custom Tkinter ##
    from CTkMessagebox import CTkMessagebox
except ImportError:
    print(f"[MessageBoxes.py] Fehler beim Import: {e}")
    exit(-810)


### Logger starten ###
getLoggerConfig()


### Funktionen ###
def calculate_box_width(message: str) -> int:
    """
    Berechnet die Breite der Nachrichtenbox basierend auf der Länge der Nachricht.

    :param message: Nachricht, deren Länge verwendet wird, um die Breite zu berechnen.
    :return: Die berechnete Breite der Box.
    """

    try:
        length = len(message)
        min_width = 250
        max_width = 1000

        match length:
            case _ if length < 20:
                return min_width
            case _ if 50 <= length < 100:
                return (min_width + max_width) / 2
            case _ if length >= 100:
                return max_width
            case _:
                return (min_width + max_width) / 2
    except Exception as e:
        log.error("[MessageBoxes.py] Fehler beim Berechnen der Boxbreite", exc_info=e)
        return (min_width + max_width) / 2

def show_info(message: str) -> None:
    """
    Eine Infobox, mit beliebiger Nachricht.

    :param message: Nachricht, die in der Infobox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    try:
        CTkMessagebox(title="Infobox", message=message, width=calculate_box_width(message))
        log.info("[MessageBoxes.py] Info-Box angezeigt: %s", message)
    except Exception as e:
        log.error("[MessageBoxes.py] Fehler beim Anzeigen der Info-Box", exc_info=e)

def show_checkmark(message: str) -> None:
    """
    Eine Checkbox, mit beliebiger Nachricht.

    :param message: Nachricht, die in der Checkbox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    try:
        CTkMessagebox(title="Thread beendet", message=message, width=calculate_box_width(message), icon="check", option_1="Okay")
        log.info("[MessageBoxes.py] Checkmark-Box angezeigt: %s", message)
    except Exception as e:
        log.error("[MessageBoxes.py] Fehler beim Anzeigen der Checkmark-Box", exc_info=e)

def show_error(message: str) -> None:
    """
    Eine Errorbox, mit 'title=Error', 'width=80' & 'icon=cancel'.

    :param message: Nachricht, die in der Errorbox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    try:
        CTkMessagebox(title="Error", message=message, width=calculate_box_width(message), icon="cancel")
        log.info("[MessageBoxes.py] Error-Box angezeigt: %s", message)
    except Exception as e:
        log.error("[MessageBoxes.py] Fehler beim Anzeigen der Error-Box", exc_info=e)