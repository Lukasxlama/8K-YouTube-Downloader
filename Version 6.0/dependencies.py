##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: dependencies.py     #
# Version: 6.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    from winreg import OpenKey, QueryValueEx, KEY_ALL_ACCESS, HKEY_CURRENT_USER, SetValueEx, REG_EXPAND_SZ, CloseKey
    from os import environ, pathsep
except ImportError:
    exit()


### Funktionen ###
def FFMPEG(PATH: str) -> None:
    """
    Fügt den FFMPEG-Ordner zur Umgebungsvariable 'Path' hinzu.

    :param PATH: Pfad, in dem sich 'ffmpeg.exe' & 'ffprobe.exe' befinden.
    :return: Liefert nichts zurück.
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