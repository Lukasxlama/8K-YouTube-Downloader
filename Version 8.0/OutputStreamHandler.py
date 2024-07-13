#####################################
# Projekt: 8K Video Downloader      #
# Dateiname: OutputStreamHandler.py #
# Version: 8.0                      #
# Autor: lukasxlama                 #
#####################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Others ##
    from customtkinter import CTk, CTkTextbox, END
    from threading import Lock, Timer
    from typing import Optional, List
    from re import match, Match
    from os import path

    import sys

except ImportError as ERR_01:
    print(f"[OutputStreamHandler.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class OutputHandler:
    _instance: Optional['OutputHandler'] = None
    _lock: Lock = Lock()

    def __new__(cls, root: Optional[CTk] = None, outputWidget: Optional[CTkTextbox] = None) -> 'OutputHandler':
        """
        Creates and returns the instance of OutputHandler.

        :param root: An CTk instance to be used as the root.
        :param outputWidget: An CTkTextbox instance to be used as the output widget.
        :return: The single instance of OutputHandler.
        """

        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OutputHandler, cls).__new__(cls)
                cls._instance.__initialized = False

            else:
                if isinstance(root, CTk):
                    cls._instance.root = root

                if isinstance(outputWidget, CTkTextbox):
                    cls._instance.outputWidget = outputWidget

        return cls._instance

    def __init__(self, root: Optional[CTk] = None, outputWidget: Optional[CTkTextbox] = None) -> None:
        """
        Creates and returns the instance of OutputHandler.

        :param root: An CTk instance to be used as the root.
        :param outputWidget: An CTkTextbox instance to be used as the output widget.
        :return: None.
        """

        if self.__initialized:
            return

        with self._lock:
            self.filePath: str = OutputHandler.getFilePath()
            self.outputWidget: CTkTextbox = outputWidget
            self.root: CTk = root
            self.lastContent: str = ""
            self.maxLines: int = 13
            self.writeLock: Lock = Lock()
            self.readLock: Lock = Lock()
            self.__initialized: bool = True

            if not path.exists(self.filePath):
                with open(self.filePath, "w", encoding='utf-8'):
                    pass

    @classmethod
    def getFilePath(cls) -> str:
        """
        Classmethod for getting the filepath.

        :return: Path to the file.
        """

        return path.join(path.dirname(path.abspath(__file__)), 'logs', '8K_STATUS.log')

    def write(self, MSG: str) -> None:
        """
        Writes a given message to the file.

        :param MSG: The message to write.
        :return: None.
        """

        with self.writeLock:
            existing_content: List[str] = self.read().split('\n\n')
            existing_content.append(MSG)

            if len(existing_content) > self.maxLines:
                existing_content = existing_content[-self.maxLines:]

            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(existing_content).strip())

    def read(self) -> str:
        """
        Reads the file content and returns it as a string.

        :return: The content of the file.
        """

        with self.readLock:
            if path.exists(self.filePath):
                with open(self.filePath, 'r', encoding='utf-8') as f:
                    return f.read()
            return ''

    def clearFile(self) -> None:
        """
        Deletes the whole content of the file.

        :return: None.
        """

        with self.writeLock:
            if path.exists(self.filePath):
                with open(self.filePath, 'w', encoding='utf-8'):
                    pass

    def hasChanged(self) -> bool:
        """
        Checks if the file has changed.

        :return: Returns a bool value indicating if the file has changed.
        """

        currContent: str = self.read()

        if currContent != self.lastContent:
            self.lastContent = currContent
            return True

        return False

    def getContent(self) -> str:
        """
        Getter for the lastContent member.

        :return: Returns the last content of the file.
        """

        return self.lastContent

    def updateConsoleFromLog(self) -> None:
        """
        Regularly checks the log file for new messages and updates the console text widget.
        Clears the log file after reading to allow dynamic deletion of old lines.

        :return: None.
        """

        if self.root is not None:
            if self.hasChanged():
                self.outputWidget.configure(state="normal")

                self.outputWidget.delete('1.0', END)
                self.outputWidget.insert(END, self.getContent())
                self.outputWidget.see(END)
                self.outputWidget.configure(state="disabled")

            self.root.after(100, self.updateConsoleFromLog)

        else:
            log.critical("[OutputStreamHandler.py@updateConsoleFromLog] Could not get self.root!")
            Timer(0.1, self.updateConsoleFromLog).start()

    def overwriteLast(self, MSG: str) -> None:
        """
        Overwrites the last content of the file.

        :param MSG: The new content of the message.
        :return: None.
        """

        with self.writeLock:
            content: List[str] = self.read().strip().split('\n\n')

            if content:
                content[-1] = MSG

            else:
                content.append(MSG)

            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(content).strip())

class StreamHandler:
    def __init__(self) -> None:
        """
        Initializes the StreamHandler, redirects the output stream and opens the SessionOutput file.

        :return: None.
        """

        self.outputHandler: OutputHandler = OutputHandler()
        self.logPath: str = path.join(path.dirname(path.abspath(__file__)), 'logs', 'SessionOutput.log')
        self.lastMSG: str = ""
        sys.stdout = self
        sys.stderr = self

        with open(self.logPath, "w", encoding='utf-8'):
            pass

    def __del__(self) -> None:
        """
        Sets the sys.stdout stream to its original value.

        :return: None.
        """

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def parseMessage(self, MSG: str) -> None:
        """
        Parses messages and writes them formatted into the GUI if they correspond to a certain type.

        :param MSG: The message to be parsed.
        :return: None.
        """

        MSG: str = MSG.strip()

        ## Sleeping Message ##
        sleeping_match: Optional[Match[str]] = match(r"\[download] Sleeping ([\d.]+) seconds \.\.\.", MSG)

        if sleeping_match:
            self.outputHandler.write(f"Sleeping {sleeping_match.group(1)} seconds")
            return

        ## Download Progress Message ##
        download_match: Optional[Match[str]] = match(r"\[download]\s+(\d+\.\d+)% of\s+~?\s*([\d.]+[A-Za-z]+)\s+"
                                                     r"at\s+([\d.]+[A-Za-z/]+)\s+ETA\s+([\d:]+)(?:\s+\(frag\s+\d+/\d+"
                                                     r"\))?", MSG)

        if download_match:
            percent: str = download_match.group(1)
            size: str = download_match.group(2)
            speed: str = download_match.group(3)
            eta: str = download_match.group(4)

            if self.lastMSG:
                self.outputHandler.overwriteLast(f"Download: {percent}% | {size} | {speed} | {eta}")

            else:
                self.outputHandler.write(f"Download: {percent}% | {size} | {speed} | {eta}")
                self.lastMSG = f"Download: {percent}% | {size} | {speed} | {eta}"

            return

        ## Download Complete Messsage ##
        completed_match: Optional[Match[str]] = match(r"\[download]\s+(\d+)% of\s+([\d.]+[A-Za-z]+)\s+in\s+([\d:]"
                                                      r"+)\s+at\s+([\d.]+[A-Za-z/]+)", MSG)

        if completed_match:
            percent: str = completed_match.group(1)
            size: str = completed_match.group(2)
            time: str = completed_match.group(3)
            speed: str = completed_match.group(4)

            self.outputHandler.write(f"Download: {percent}% | {size} | {speed} | {time}")
            self.lastMSG = ""

            return

        ## Other Filters here ##

    def write(self, MSG: str) -> None:
        """
        Writes a message to the log file and parses it.

        :param MSG: The message to be logged and parsed. (from sys.stdout)
        :return: None.
        """

        with open(self.logPath, "a", encoding='utf-8') as f:
            f.write(f"{MSG}")

        self.parseMessage(MSG)

    def flush(self) -> None:
        """
        Flushes the internal buffer. (not implemented yet)

        :return: None.
        """

        pass