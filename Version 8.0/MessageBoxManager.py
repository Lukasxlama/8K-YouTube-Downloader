##################################
# Project: 8K Video Downloader   #
# Filename: MessageBoxManager.py #
# Version: 8.0                   #
# Author: lukasxlama             #
##################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Others ##
    from CTkMessagebox import CTkMessagebox
    from typing import Optional

except ImportError as ERR_01:
    print(f"[MessageBoxManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class MessageBoxManager:
    """
    Configures Messageboxes for the GUI application.

    This class provides methods to generate different level of boxes.
    """

    @staticmethod
    def calcBoxWidth(MSG: str) -> float:
        """
        Calculates the width of the message box based on the length of the message.

        :param MSG: The message whose length is used to determine the box width.
        :return: The calculated width of the box.
        """

        min_width: int = 250
        max_width: int = 1000

        try:
            length: int = len(MSG)

            if length < 20:
                return min_width

            elif 50 <= length < 100:
                return (min_width + max_width) / 2

            elif length >= 100:
                return max_width

            else:
                return (min_width + max_width) / 2

        except Exception as ERR_02:
            log.error("[MessageBoxManager.py] Error calculating box width", exc_info=ERR_02)
            return (min_width + max_width) / 2

    def showMessage(self, MSG: str, TITLE: str, ICO: Optional[str] = None, OPT1: Optional[str] = None) -> None:
        """
        Displays a message box with a custom message, title, and optional icon and option.

        :param MSG: The message to display in the message box.
        :param TITLE: The title of the message box.
        :param ICO: The icon to display in the message box (default is None).
        :param OPT1: The first option button in the message box (default is None).
        :return: None.
        """

        try:
            CTkMessagebox(title=TITLE, message=MSG, width=self.calcBoxWidth(MSG), icon=ICO, option_1=OPT1)
            log.info("[MessageBoxManager.py] %s box displayed: %s", TITLE, MSG)

        except Exception as ERR_03:
            log.error("[MessageBoxManager.py] Error displaying %s box", TITLE.lower(), exc_info=ERR_03)

    def showInfo(self, MSG: str) -> None:
        """
        Displays an info box with a custom message.

        :param MSG: The message to display in the info box.
        :return: None.
        """

        self.showMessage(MSG=MSG, TITLE="Info", ICO="info", OPT1="Okay")

    def showCheckmark(self, MSG: str) -> None:
        """
        Displays a checkmark box with a custom message.

        :param MSG: The message to display in the checkmark box.
        :return: None.
        """

        self.showMessage(MSG=MSG, TITLE="Finished", ICO="check", OPT1="Okay")

    def showError(self, MSG: str) -> None:
        """
        Displays an error box with a custom message.

        :param MSG: The message to display in the error box.
        :return: None.
        """

        self.showMessage(MSG=MSG, TITLE="Error", ICO="cancel", OPT1="Okay")
