##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: Dependencies.py     #
# Version: 7.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggerConfig import getLoggerConfig
    import logging as log

    ## Betriebssystem- und Registrierungseditor ##
    from winreg import OpenKey, QueryValueEx, KEY_ALL_ACCESS, HKEY_CURRENT_USER, SetValueEx, REG_EXPAND_SZ, CloseKey
    from os import path, environ, pathsep
    import sys
except ImportError:
    print(f"[Dependencies.py] Fehler beim Import: {e}")
    sys.exit(-810)


### Logger starten ###
getLoggerConfig()


### Klassen ###
class DependenciesError(Exception):
    """
    Eine Exception-Klasse, die bei Fehlern im Bearbeiten der Registry geworfen wird.
    """

    def __init__(self, message="Fehler beim Bearbeiten der Registry!"):
        self.message = message
        super().__init__(self.message)


### Funktionen ###
def FFMPEG(PATH: str) -> None:
    """
    Fügt den FFMPEG-Ordner zur Umgebungsvariable 'Path' hinzu.

    :param PATH: Pfad, in dem sich 'ffmpeg.exe' & 'ffprobe.exe' befinden.
    :return: Liefert nichts zurück.
    """

    ffmpeg_path = path.join(PATH, 'ffmpeg.exe')
    ffprobe_path = path.join(PATH, 'ffprobe.exe')

    try:
        if not path.isfile(ffmpeg_path) or not path.isfile(ffprobe_path):
            raise DependenciesError(f"FFMPEG oder FFprobe nicht gefunden im Pfad: {PATH}")

        key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
        value, _ = QueryValueEx(key, 'Path')
        paths = value.split(pathsep)

        if PATH in paths:
            return

        paths.append(PATH)
        new_value = pathsep.join(paths)
        SetValueEx(key, 'Path', 0, REG_EXPAND_SZ, new_value)
        CloseKey(key)
        environ['PATH'] += pathsep + PATH
        log.info("FFMPEG-Pfad zur Umgebungsvariable 'Path' hinzugefügt.")

    except DependenciesError:
        log.critical(f"FFMPEG oder FFprobe nicht gefunden im Pfad: {PATH}")
        sys.exit(-810)

    except Exception as e:
        log.critical(f"Fehler beim Hinzufügen von FFMPEG zum Path: {e}")
        sys.exit(-810)