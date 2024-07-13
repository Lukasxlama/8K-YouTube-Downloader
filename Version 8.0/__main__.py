##################################
# Projekt: 8K Video Downloader   #
# Dateiname: __main__.py         #
# Version: 8.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Others ##
    from GUIManager import GUIManager, OutputHandler
    from MessageBoxManager import MessageBoxManager
    from subprocess import run, CalledProcessError
    from DownloadManager import DownloadManager
    from LinkManager import LinkManager
    from os import path

except ImportError as ERR_01:
    print(f"[__main__.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Exit Codes ###
EXIT_SUCCESS: int = 0
EXIT_SHUTDOWN: int = 1000
EXIT_IMPORT_ERROR: int = -810
EXIT_KEYBOARD_INTERRUPT: int = 130

### Start Main Program ###
if __name__ == '__main__':
    try:
        shutdown: bool = False
        GUIManager()

    except KeyboardInterrupt:
        raise SystemExit(EXIT_KEYBOARD_INTERRUPT)

    except SystemExit as ERR_02:
        if ERR_02.code == EXIT_SUCCESS:
            log.info(f"[__main__.py] Expected program shutdown with exit code {ERR_02.code}. Bye 👋")

        elif ERR_02.code == EXIT_SHUTDOWN:
            shutdown = True

        elif ERR_02.code == EXIT_KEYBOARD_INTERRUPT:
            log.info(f"[__main__.py] Program interrupted by user with exit code {ERR_02.code}")

        else:
            log.critical(f"[__main__.py] Unexpected program shutdown with exit code {ERR_02.code}")

    except Exception as ERR_03:
        log.critical(f"[__main__.py] Unexpected program shutdown: {str(ERR_03)}")

    finally:
        if path.exists(OutputHandler.getFilePath()):
            with open(OutputHandler.getFilePath(), 'w'):
                pass

        if shutdown:
            try:
                run(['shutdown', '/s', '/f', '/t', '30'], check=True)

            except CalledProcessError as ERR_04:
                log.error(f"[__main__.py] Error during shutdown: {ERR_04}")
