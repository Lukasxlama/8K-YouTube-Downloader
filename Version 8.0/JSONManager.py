##################################
# Project: 8K Video Downloader   #
# Filename: JSONManager.py       #
# Version: 8.0                   #
# Author: lukasxlama             #
##################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Custom Modules ##
    from LinkManager import LinkManager

    ## Others ##
    from typing import List, Tuple, Generator
    from json import load, JSONDecodeError

except ImportError as ERR_01:
    print(f"[JSONManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class JSONManager:
    """
    A class to extract URLs from JSON files.

    The valid JSON format:

    {
        "8K_DOWNLOAD":
        [
            "URL_1",
            "URL_2",
            "URL_3",
            ...
            "URL_n"
        ]
    }
    """

    def __init__(self, JSON_PATH: str = None) -> None:
        """
        Initializes the JSONManager class with the provided JSON path.

        :param JSON_PATH: The path to the JSON file.
        :return: None.
        """

        self.linkManager: LinkManager = LinkManager()
        self.jsonPath: str = JSON_PATH
        self.links: List[str] = []

    def setJSON(self, JSON_PATH: str) -> None:
        """
        Sets the JSON path and loads the URLs.

        :param JSON_PATH: The path to the JSON file.
        :return: None.
        """

        self.jsonPath = JSON_PATH
        self._loadURLs()

    def _loadURLs(self) -> None:
        """
        Loads URLs from the JSON file.

        :return: None.
        """

        if not self.validateJSONFormat():
            raise JSONDecodeError("Invalid JSON format", 0, 0)

        if not self.jsonPath:
            raise ValueError("No JSON path provided")

        with open(self.jsonPath, 'r') as file:
            self.links = load(file).get('8K_DOWNLOAD', [])

    def validateJSONFormat(self) -> bool:
        """
        Validates the JSON format.

        :return: bool: True if the JSON format is valid, False otherwise.
        """

        if not self.jsonPath:
            raise ValueError("No JSON path provided")

        try:
            with open(self.jsonPath, 'r') as f:
                data: Dict[str, List[str]] = load(f)

            if isinstance(data, dict) and '8K_DOWNLOAD' in data:
                if isinstance(data['8K_DOWNLOAD'], list):
                    if all(isinstance(item, str) for item in data['8K_DOWNLOAD']):
                        return True

            else:
                return False

        except (JSONDecodeError, FileNotFoundError):
            return False

    def validateJSONURLs(self) -> Tuple[bool, str]:
        """
        Validates the URLs in the JSON file.

        :return: tuple: (bool, str) - True if all URLs are valid, False otherwise with the first invalid URL.
        """

        for url in self.getURLs():
            if not self.linkManager.isUrlValid(url):
                return False, url

        return True, ""

    def getURLs(self) -> Generator[str, None, None]:
        """
        Generator function to get the list of URLs from the JSON file.

        :return: A generator that yields URLs.
        """

        if len(self.links) == 0:
            raise ValueError("URL List is empty.")

        for link in self.links:
            yield link
