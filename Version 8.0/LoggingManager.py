##################################
# Project: 8K Video Downloader   #
# Filename: LoggingManager.py    #
# Version: 8.0                   #
# Author: lukasxlama             #
##################################

### Imports ###
try:
    ## Logging ##
    from logging import INFO, DEBUG, ERROR, CRITICAL, WARNING, Formatter, getLogger, Filter, LogRecord, Logger
    from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

    ## Others ##
    from os import path, makedirs
    from typing import Optional

except ImportError as ERR_01:
    print(f"[LoggingManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Classes ###
class LevelFilter(Filter):
    def __init__(self, LEVEL: int) -> None:
        super().__init__()
        self.level: int = LEVEL

    def filter(self, record: LogRecord) -> bool:
        return record.levelno == self.level

class LoggingManager:
    """
    Configures logging for the entire application.

    This class provides methods to set up different levels of logging handlers.
    """

    initialized: bool = False
    logger: Optional[Logger] = None

    def __init__(self, LOG_DIR: str = f"{path.dirname(path.abspath(__file__))}/logs") -> None:
        """
        Initializes the LoggingManager with the directory to store log files.

        :param LOG_DIR: The directory where the log files will be stored.
                        Defaults to a 'logging' folder in the same directory as this script.
        :return: None.
        """

        self.logDir: str = LOG_DIR

        if not LoggingManager.initialized:
            self.setupLogging()
            LoggingManager.initialized = True

    def setupLogging(self) -> None:
        """
        Sets up logging handlers for different levels of logging: INFO, ERROR, and CRITICAL.

        :return: None
        """

        if LoggingManager.initialized:
            return

        try:
            if not path.exists(self.logDir):
                makedirs(self.logDir)

            LoggingManager.logger = getLogger('8K_LOGGER')
            LoggingManager.logger.setLevel(DEBUG)

            ## INFO Handler ##
            info_handler: RotatingFileHandler = RotatingFileHandler(
                filename=path.join(self.logDir, 'info.log'),
                maxBytes=5_242_880,
                backupCount=5,
                encoding='utf-8'
            )

            info_handler.setLevel(INFO)
            info_handler.addFilter(LevelFilter(INFO))
            info_handler.setFormatter(Formatter('%(asctime)s - INFO: %(message)s', '%Y-%m-%d %H:%M:%S'))
            LoggingManager.logger.addHandler(info_handler)

            ## DEBUG Handler ##
            debug_handler: RotatingFileHandler = RotatingFileHandler(
                filename=path.join(self.logDir, 'debug.log'),
                maxBytes=5_242_880,
                backupCount=5,
                encoding='utf-8'
            )

            debug_handler.setLevel(DEBUG)
            debug_handler.addFilter(LevelFilter(DEBUG))
            debug_handler.setFormatter(Formatter('%(asctime)s - DEBUG: %(message)s', '%Y-%m-%d %H:%M:%S'))
            LoggingManager.logger.addHandler(debug_handler)

            ## ERROR Handler ##
            error_handler: RotatingFileHandler = RotatingFileHandler(
                filename=path.join(self.logDir, 'error.log'),
                maxBytes=5_242_880,
                backupCount=5,
                encoding='utf-8'
            )

            error_handler.setLevel(ERROR)
            error_handler.addFilter(LevelFilter(ERROR))
            error_handler.setFormatter(Formatter('%(asctime)s - ERROR | %(message)s\n'
                                                 'Stack Trace:\n%(exc_info)s\n\n', '%Y-%m-%d %H:%M:%S'))
            LoggingManager.logger.addHandler(error_handler)

            ## CRITICAL Handler ##
            critical_handler: RotatingFileHandler = RotatingFileHandler(
                filename=path.join(self.logDir, 'critical.log'),
                maxBytes=5_242_880,
                backupCount=5,
                encoding='utf-8'
            )

            critical_handler.setLevel(CRITICAL)
            critical_handler.addFilter(LevelFilter(CRITICAL))
            critical_handler.setFormatter(Formatter('%(asctime)s - CRITICAL: %(message)s', '%Y-%m-%d %H:%M:%S'))
            LoggingManager.logger.addHandler(critical_handler)

            ## WARNING Handler ##
            warning_handler: RotatingFileHandler = RotatingFileHandler(
                filename=path.join(self.logDir, 'warning.log'),
                maxBytes=5_242_880,
                backupCount=5,
                encoding='utf-8'
            )

            warning_handler.setLevel(WARNING)
            warning_handler.addFilter(LevelFilter(WARNING))
            warning_handler.setFormatter(Formatter('%(asctime)s - WARNING: %(message)s', '%Y-%m-%d %H:%M:%S'))
            LoggingManager.logger.addHandler(warning_handler)

        except Exception as ERR_02:
            print(f"[LoggingManager.py] Error configuring logging: {ERR_02}")
            raise SystemExit(-810)

    @classmethod
    def getLogger(cls) -> Logger:
        """
        Returns the configured logger.

        :return: The logger instance
        """

        return cls.logger
