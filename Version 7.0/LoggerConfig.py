##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: LoggerConfig.py     #
# Version: 7.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from logging import INFO, ERROR, CRITICAL, Formatter, getLogger
    from logging.handlers import RotatingFileHandler

    ## Pfad- und Dateiverwaltung ##
    from os import path, makedirs
    import sys
except ImportError:
    print(f"[LoggerConfig.py] Fehler beim Import: {e}")
    sys.exit(-810)


### Funktionen ###
def getLoggerConfig(PATH: str = f"{path.dirname(path.abspath(__file__))}/logging") -> None:
    """
    Konfiguriert das Logging für die gesamte Anwendung.

    :param PATH: Das Verzeichnis, in dem die Log-Dateien gespeichert werden sollen.
    :return: None
    """

    try:
        if not path.exists(PATH):
            makedirs(PATH)

        info_handler = RotatingFileHandler(filename=path.join(PATH, 'info.log'), maxBytes=5_242_880, backupCount=5, encoding='utf-8')
        info_handler.setLevel(INFO)
        info_handler.setFormatter(Formatter('%(asctime)s - INFO: %(message)s', '%Y-%m-%d %H:%M:%S'))

        error_handler = RotatingFileHandler(filename=path.join(PATH, 'error.log'), maxBytes=5_242_880, backupCount=5, encoding='utf-8')
        error_handler.setLevel(ERROR)
        error_handler.setFormatter(Formatter('%(asctime)s - ERROR | %(message)s\nStack Trace:\n%(exc_info)s\n\n', '%Y-%m-%d %H:%M:%S'))

        critical_handler = RotatingFileHandler(filename=path.join(PATH, 'critical.log'), maxBytes=5_242_880, backupCount=5, encoding='utf-8')
        critical_handler.setLevel(CRITICAL)
        critical_handler.setFormatter(Formatter('%(asctime)s - CRITICAL: %(message)s', '%Y-%m-%d %H:%M:%S'))

        logger = getLogger()
        logger.setLevel(INFO)
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)
        logger.addHandler(critical_handler)
    except Exception as e:
        print(f"[LoggerConfig.py] Fehler beim Konfigurieren des Loggings: {e}")