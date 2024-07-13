##################################
# Projekt: 8K Video Downloader   #
# Dateiname: Dependencies.py     #
# Version: 8.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Others ##
    from winreg import OpenKey, QueryValueEx, KEY_ALL_ACCESS, HKEY_CURRENT_USER, SetValueEx, REG_EXPAND_SZ, CloseKey
    from os import path, environ, pathsep

except ImportError as ERR_01:
    print(f"[Dependencies.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class DependenciesManager:
    """
    A class to manage the addition and removal of FFmpeg to the system's 'Path' environment variable.

    This class provides class methods to add and remove the FFmpeg directory from the 'Path'
    environment variable on a Windows system. This is useful for ensuring that FFmpeg tools
    can be accessed from the command line without specifying the full path.
    """

    @classmethod
    def addFFmpegToPath(cls, PATH: str) -> None:
        """
        Adds the FFmpeg folder to the 'Path' environment variable.

        :param PATH: Path containing 'ffmpeg.exe' & 'ffprobe.exe'.
        :return: None.
        """

        ffmpeg_path: str = path.join(PATH, 'ffmpeg.exe')
        ffprobe_path: str = path.join(PATH, 'ffprobe.exe')

        try:
            if not path.isfile(ffmpeg_path) or not path.isfile(ffprobe_path):
                raise Exception(f"FFmpeg and/or FFprobe not found in path: {PATH}")

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
            log.info("[Dependencies.py@addFFmpegToPath] FFmpeg path added to the 'Path' environment variable.")

        except Exception as ERR_02:
            log.critical(f"[Dependencies.py@addFFmpegToPath] Error adding FFmpeg to the path: {ERR_02}")
            raise SystemExit(-810)

    @classmethod
    def removeFFmpegFromPath(cls, PATH: str) -> None:
        """
        Removes the FFmpeg folder from the 'Path' environment variable.

        :param PATH: Path containing 'ffmpeg.exe' & 'ffprobe.exe'.
        :return: None.
        """

        try:
            key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
            value, _ = QueryValueEx(key, 'Path')
            paths = value.split(pathsep)

            if PATH not in paths:
                return

            paths.remove(PATH)
            new_value = pathsep.join(paths)
            SetValueEx(key, 'Path', 0, REG_EXPAND_SZ, new_value)
            CloseKey(key)
            environ['PATH'] = pathsep.join(p for p in environ['PATH'].split(pathsep) if p != PATH)
            log.info("[Dependencies.py@removeFFmpegFromPath] FFmpeg path removed from the 'Path' environment variable.")

        except Exception as ERR_03:
            log.critical(f"[Dependencies.py@removeFFmpegFromPath] Error removing FFmpeg from the path: {ERR_03}")
            raise SystemExit(-810)
