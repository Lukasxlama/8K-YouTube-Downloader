##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: messageboxes.py     #
# Version: 6.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    from CTkMessagebox import CTkMessagebox
except ImportError:
    exit()


### Funktionen ###
def show_info(message: str) -> None:
    """
    Eine Infobox, mit 'title=Infobox' & 'width=80'.

    :param message: Nachricht, die in der Infobox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    CTkMessagebox(title="Infobox", message=message, width=80)

def show_checkmark(message: str) -> None:
    """
    Eine Checkbox, mit 'title=Thread beendet', 'width=80', 'icon=check' & 'option_1=Okay'.

    :param message: Nachricht, die in der Checkbox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    CTkMessagebox(title="Thread beendet", message=message, width=80, icon="check", option_1="Okay")

def show_error(message: str) -> None:
    """
    Eine Errorbox, mit 'title=Error', 'width=80' & 'icon=cancel'.

    :param message: Nachricht, die in der Errorbox angezeigt wird.
    :return: Liefert nichts zurück.
    """

    CTkMessagebox(title="Error", message=message, width=80, icon="cancel")