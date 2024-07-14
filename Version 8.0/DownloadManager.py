##################################
# Project: 8K Video Downloader   #
# Filename: DownloadManager.py   #
# Version: 8.0                   #
# Author: lukasxlama             #
##################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Custom Modules ##
    from PostprocessorManager import (YouTubePostprocessorManager, TwitchPostprocessorManager,
                                      SoundcloudPostprocessorManager, PodcastdePostprocessorManager)
    from DependenciesManager import DependenciesManager
    from LinkManager import LinkManager
    from JSONManager import JSONManager

    if __name__ != '__main__':
        from OutputStreamHandler import OutputHandler

    ## Others ##
    from yt_dlp.networking.exceptions import HTTPError as YTDLP_HTTPError
    from yt_dlp.utils import DownloadError as YTDLP_DownloadError
    from typing import List, Dict, Any, Optional
    from os import path, makedirs
    from bs4 import BeautifulSoup
    from datetime import datetime
    from yt_dlp import YoutubeDL
    from bs4.element import Tag
    from re import sub, search
    from requests import get

except ImportError as ERR_01:
    print(f"[DownloadVideo.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class PodcastdeWorkaround:
    """
    A class to handle the retrieval of podcast episode URLs from the podcast.de archive.

    This class provides methods to fetch all episode URLs from a given podcast URL,
    handling pagination and extracting URLs from each page.
    """

    def __init__(self, URL: str) -> None:
        """
        Initializes the PodcastdeWorkaround with the given URL.

        :param URL: The base URL of the podcast to retrieve episodes from.
        :return: None.
        """

        self.url: str = URL
        self.baseURL: str = URL.split('?')[0]

    def getEpisodeURLs(self) -> List[str]:
        """
        Retrieves a list of episode URLs from the podcast archive.

        :return: A list of unique episode URLs in ascended order.
        """

        urls: List[str] = []

        for page in range(1, self.getNumberOfPages(self.url) + 1):
            urls.extend(self.getEpisodesFromPages(f"{self.baseURL}?page={page}"))

        return list(reversed(dict.fromkeys(urls)))

    @staticmethod
    def getEpisodesFromPages(URL: str) -> List[str]:
        """
        Retrieves episode URLs from the provided list of page URLs.

        :param URL: A page URL from which to extract episode URLs.
        :return: A list of episode URLs extracted from the provided pages.
        """

        soup: BeautifulSoup = BeautifulSoup(get(URL).content, 'html.parser')
        return [link['href'] for link in soup.select('.episode-list .row a')]

    @staticmethod
    def getNumberOfPages(URL: str) -> int:
        """
        Retrieves the total number of pages for a given podcast URL.

        :param URL: The URL of the podcast page to analyze.
        :return: The total number of pages found.
        """

        soup: BeautifulSoup = BeautifulSoup(get(URL).content, 'html.parser')
        pagination: Tag = soup.select('.pagination .page-item a')

        if not pagination:
            return 1

        return int(search(r'page=(\d+)', pagination[-2]['href']).group(1))

class DownloadManager:
    """
    The DownloadManager class handles downloading media from various platforms using yt-dlp and
    post-processing the downloaded files.
    """

    def __init__(self) -> None:
        """
        Initializes the DownloadManager class, sets up dependencies, and initializes necessary managers.

        :return: None
        """

        DependenciesManager.addFFmpegToPath(path.join(path.dirname(path.abspath(__file__)), 'ffmpeg', 'bin'))

        self.youtubePostprocessorManager: YouTubePostprocessorManager = YouTubePostprocessorManager()
        self.twitchPostprocessorManager: TwitchPostprocessorManager = TwitchPostprocessorManager()
        self.soundcloudPostprocessorManager: SoundcloudPostprocessorManager = SoundcloudPostprocessorManager()
        self.podcastdePostprocessorManager: PodcastdePostprocessorManager = PodcastdePostprocessorManager()

        if __name__ != '__main__':
            self.outputHandler: OutputHandler = OutputHandler()

        self.linkManager: LinkManager = LinkManager()
        self.jsonManager: JSONManager = JSONManager()

        self._downloadProgress: float = 0
        self.downloadOptions: Optional[Dict[str, Any]] = None

    async def setOptions(self, OPT_DICT: Dict[str, Any]) -> None:
        """
        Validates and sets the options for the download manager.\n
        The following dictionary entries are valid:
            - URL: The URL of the medium to be downloaded
            - PATH: The path where the downloaded files are to be saved
            - FLAG: Specifies what should be downloaded for URLs with video and playlist ID (valid options are 'video' & 'playlist')
            - QUAL: A tuple that specifies the quality of the media to be downloaded. It is structured as follows: (AUDIO, (AUDIO, VIDEO))
            - POSTPROCESS: A bool that specifies whether the downloaded files are to be processed directly into the finished medium
            - THUMBNAIL: A bool that specifies whether a preview image of the medium should be downloaded.
            - SUBTITLES: A bool that specifies whether subtitles should be downloaded. Currently only works for YouTube in MP4 format.
            - TIMEOUT: Specifies how long to wait after a download. Helpful if there is rate limiting
            - SILENT_OUTPUT: A bool that specifies whether additional information should be output during the download
            - USE_JSON: A bool that specifies whether a JSON file should be used for passing the URLs.
            - JSON_PATH: A string that specifies the path to the JSON file to be used for passing the URLs.

        :param OPT_DICT: Dictionary of input options.
        :return: None
        """

        self.downloadOptions = await self.validateOptions(OPT_DICT)

    def progressHook(self, STATUS: Dict[str, Any]) -> None:
        """
        Updates the download progress based on the status dictionary provided by yt-dlp.

        :param STATUS: A dictionary provided by yt-dlp containing information about the current status of the download.
        :return: None
        """

        if STATUS['status'] == 'downloading':
            self._downloadProgress = float(sub(r".*?(\d+\.\d+%).*",
                                               r"\1", STATUS['_percent_str']).replace("%", ""))

        elif STATUS['status'] == 'finished':
            self._downloadProgress = 100.0

    @property
    def downloadProgress(self) -> float:
        """
        Returns the current download progress.

        :return: Download progess as a float.
        """

        return self._downloadProgress

    async def validateOptions(self, OPT_DICT: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and sanitizes the input options.

        :param OPT_DICT: Dictionary of input options.
        :return: Dictionary of validated and sanitized options.
        """
        defaults: Dict[str, None] = {
            'URL': None,
            'PATH': None,
            'FLAG': None,
            'FORMAT': None,
            'QUAL': None,
            'POSTPROCESS': None,
            'THUMBNAIL': None,
            'SUBTITLES': None,
            'TIMEOUT': None,
            'SILENT_OUTPUT': None,
            'USE_JSON': None,
            'JSON_PATH': None
        }

        OPT_DICT: Dict[str, Any] = {key.upper(): value for key, value in OPT_DICT.items()}
        filled_dict: Dict[str, Any] = {**defaults, **OPT_DICT}

        if not filled_dict.get('USE_JSON') and not filled_dict.get('URL'):
            raise ValueError("The 'URL' option is required.")

        if not filled_dict.get('USE_JSON') and not self.linkManager.isUrlValid(filled_dict.get('URL'))[0]:
            raise ValueError("The URL is not valid.")

        if not filled_dict.get('PATH'):
            filled_dict['PATH'] = fr"./8kdownloads/{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}"

        if not path.exists(filled_dict['PATH']):
            makedirs(filled_dict['PATH'])

        if filled_dict.get('FLAG') not in ['video', 'playlist']:
            raise ValueError("Invalid FLAG. Allowed values are 'video' and 'playlist'.")

        if not filled_dict.get('FLAG'):
            filled_dict['FLAG'] = 'video'

        if filled_dict.get('FORMAT') not in ['mp4', 'mp3']:
            raise ValueError("Invalid FORMAT. Allowed values are 'mp4' and 'mp3'.")

        if not filled_dict.get('FORMAT'):
            filled_dict['FORMAT'] = 'mp4'

        if not filled_dict.get('QUAL'):
            filled_dict['QUAL'] = (320, (320, 4320))

        if not isinstance(filled_dict.get('QUAL'), tuple) or len(filled_dict.get('QUAL')) != 2 or \
                not isinstance(filled_dict.get('QUAL')[0], int) or not isinstance(filled_dict.get('QUAL')[1], tuple) or \
                len(filled_dict.get('QUAL')[1]) != 2 or not isinstance(filled_dict.get('QUAL')[1][0], int) or \
                not isinstance(filled_dict.get('QUAL')[1][1], int):
            raise ValueError("Invalid QUAL format. Expected format is (AUDIO, (AUDIO, VIDEO)) with integers.")

        if filled_dict.get('POSTPROCESS') is None:
            filled_dict['POSTPROCESS'] = True

        if not isinstance(filled_dict.get('POSTPROCESS'), bool):
            raise ValueError("Invalid POSTPROCESS value. It must be a boolean.")

        if filled_dict.get('THUMBNAIL') is None:
            filled_dict['THUMBNAIL'] = True

        if not isinstance(filled_dict.get('THUMBNAIL'), bool):
            raise ValueError("Invalid THUMBNAIL value. It must be a boolean.")

        if filled_dict.get('SUBTITLES') is None or filled_dict.get('FORMAT') == 'mp3':
            filled_dict['SUBTITLES'] = False

        if not isinstance(filled_dict.get('SUBTITLES'), bool):
            raise ValueError("Invalid SUBTITLES value. It must be a boolean.")

        if filled_dict.get('TIMEOUT') is None:
            filled_dict['TIMEOUT'] = 10

        if not isinstance(filled_dict.get('TIMEOUT'), int) or filled_dict.get('TIMEOUT') < 0:
            raise ValueError("Invalid TIMEOUT value. It must be a non-negative integer.")

        if filled_dict.get('SILENT_OUTPUT') is None:
            filled_dict['SILENT_OUTPUT'] = False

        if not isinstance(filled_dict.get('SILENT_OUTPUT'), bool):
            raise ValueError("Invalid SILENT_OUTPUT value. It must be a boolean.")

        if filled_dict.get('USE_JSON'):
            if not path.exists(filled_dict.get('JSON_PATH')) or not path.isfile(filled_dict.get('JSON_PATH')) or \
                    not filled_dict.get('JSON_PATH').lower().endswith(".json"):
                raise ValueError("The given path does not refer to a JSON file.")

            self.jsonManager.setJSON(filled_dict.get('JSON_PATH'))
            if not self.jsonManager.validateJSONFormat():
                raise ValueError("The format of the given JSON file is invalid.")

            isValid, invalidURL = self.jsonManager.validateJSONURLs()
            if not isValid:
                raise ValueError(f"At least one link of the JSON file is invalid: {invalidURL}")

        return filled_dict

    def determineFormatSettings(self) -> Dict[str, str]:
        """
        Determines the download settings based on format, quality, and platform.

        :return: Dictionary with format settings for yt-dlp.
        """

        settings = {}

        if self.downloadOptions.get('LINK_PLATFORM') in ['youtube', 'twitch']:
            if self.downloadOptions.get('FORMAT') == 'mp4':
                settings.update({'format': f'bestvideo[height<={self.downloadOptions.get("QUAL")[1][1]}]+bestaudio'
                                           f'[abr<={self.downloadOptions.get("QUAL")[1][0]}]/best'})

            elif self.downloadOptions.get('FORMAT') == 'mp3':
                settings.update({'format': f'bestaudio[abr<={self.downloadOptions.get("QUAL")[0]}]/best'})

        elif self.downloadOptions.get('LINK_PLATFORM') in ['soundcloud', 'podcastde']:
            if self.downloadOptions.get('FORMAT') == "mp4":
                log.info(f"Warning - {self.downloadOptions.get('LINK_PLATFORM')} does not support 'mp4' format. Using "
                         f"'mp3' format instead.")

            settings.update({'format': f'bestaudio[abr<={self.downloadOptions.get("QUAL")[0]}]/best'})

        # add other platforms here!

        else:
            raise ValueError(f"Unsupported platform: {self.downloadOptions.get('LINK_PLATFORM')}")

        return settings

    async def downloadVideo(self) -> bool:
        """
        Downloads media from various platforms and saves them locally. Can also post-process the files directly.

        :return: The success of the download.
        """

        if not self.downloadOptions:
            log.error("[DownloadManager.py@downloadVideo] The options must first be set with "
                      "DownloadManager().setOptions()")
            return False

        downloadURLs: List[str] = [self.downloadOptions.get('URL')]

        if self.downloadOptions.get('USE_JSON'):
            self.jsonManager.setJSON(self.downloadOptions.get('JSON_PATH'))
            downloadURLs = list(self.jsonManager.getURLs())

        allDownloadsSuccessful: bool = True
        rateLimit: bool = False

        for currentURL in downloadURLs:
            self.downloadOptions.update({'URL': currentURL})
            mediaInfo: Dict[str, Any] = await self.linkManager.getMediaInfo(self.downloadOptions.get('URL'))

            if not mediaInfo.get('LINK_SUCCESS', False):
                log.error(f"[DownloadManager.py@downloadVideo] {mediaInfo.get('LINK_ERROR', 'Unknown error')}")
                allDownloadsSuccessful = False
                continue

            self.downloadOptions.update(**mediaInfo)
            log.debug(f"[DownloadManager.py@downloadVideo] Options: {self.downloadOptions}")

            try:
                ytdlpOptions: Dict[str, Any] = \
                {
                    'outtmpl': path.join(self.downloadOptions.get('PATH'), '%(title)s.8kdownload.%(ext)s') if
                    self.downloadOptions.get('POSTPROCESS') else path.join(self.downloadOptions.get('PATH'),
                                                                           '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progressHook] if not __name__ == '__main__' else [],
                    'writethumbnail': self.downloadOptions.get('THUMBNAIL', False),
                    'sleep_interval': 1,
                    'max_sleep_interval': self.downloadOptions.get('TIMEOUT', 15),
                    'verbose': not self.downloadOptions.get('SILENT_OUTPUT', False),
                    'quiet': self.downloadOptions.get('SILENT_OUTPUT', False),
                    'ffmpeg_location': path.join(path.dirname(path.abspath(__file__)), 'ffmpeg', 'bin'),
                    'socket_timeout': 10,
                    'retries': 3,
                    'noplaylist': self.downloadOptions.get('FLAG') != 'playlist',
                    'writesubtitles': self.downloadOptions.get('SUBTITLES', False) if
                    self.downloadOptions.get('LINK_PLATFORM')
                    == 'youtube' else False,
                    'subtitleslangs': ['all', '-live_chat'] if self.downloadOptions.get('SUBTITLES', False) else None,
                    **self.determineFormatSettings()
                }

                if self.downloadOptions.get('LINK_TYPE') == 'podcast':
                    with YoutubeDL(ytdlpOptions) as ytdlp:
                        ytdlp.download(PodcastdeWorkaround(self.downloadOptions.get('URL')).getEpisodeURLs())

                else:
                    with YoutubeDL(ytdlpOptions) as ytdlp:
                        ytdlp.download([self.downloadOptions.get('URL')])

                if not self.downloadOptions.get('POSTPROCESS', False):
                    continue

                match self.downloadOptions.get('LINK_PLATFORM'):
                    case 'youtube':
                        if self.outputHandler is not None:
                            self.outputHandler.write("Using YouTube-Postprocessor ...")

                        self.youtubePostprocessorManager.setOptions(self.downloadOptions)
                        await self.youtubePostprocessorManager.processFiles()

                    case 'twitch':
                        if self.outputHandler is not None:
                            self.outputHandler.write("Using Twitch-Postprocessor ...")

                        self.twitchPostprocessorManager.setOptions(self.downloadOptions)
                        await self.twitchPostprocessorManager.processFiles()

                    case 'soundcloud':
                        if self.outputHandler is not None:
                            self.outputHandler.write("Using SoundCloud-Postprocessor ...")

                        self.soundcloudPostprocessorManager.setOptions(self.downloadOptions)
                        await self.soundcloudPostprocessorManager.processFiles()

                    case 'podcastde':
                        if self.outputHandler is not None:
                            self.outputHandler.write("Using Podcastde-Postprocessor ...")

                        self.podcastdePostprocessorManager.setOptions(self.downloadOptions)
                        await self.podcastdePostprocessorManager.processFiles()

                    case _:
                        log.error(f"[DownloadManager.py@downloadVideo] Failed postprocessing (default case)")
                        raise ValueError(f"Unsupported platform: {self.downloadOptions.get('LINK_PLATFORM')}")

            except (YTDLP_HTTPError, YTDLP_DownloadError) as ERR_02:
                if "HTTP Error 403: Forbidden" in ERR_02.msg:
                    log.error(f"[DownloadManager.py@downloadVideo] Failed to fetch resources due to rate limiting.")
                    if self.outputHandler is not None:
                        self.outputHandler.write("Rate Limiting detected, skipping download ...")

                    rateLimit = True
                    continue

                else:
                    raise ERR_02

            except Exception as ERR_03:
                log.critical(f"[DownloadManager.py@downloadVideo] Critical error during download: {ERR_03}",
                             exc_info=True)
                allDownloadsSuccessful = False
                continue

        if rateLimit:
            raise ValueError("Aborted due to rate limiting")

        else:
            return allDownloadsSuccessful

if __name__ == '__main__':
    """
    It is also possible to use the program without the GUI.
    The following code describes how this works.
    """

    from time import time  # time from the time module to measure the runtime
    from asyncio import run  # run from the asyncio module to start the asynchronous download

    # All options that are passed to the DownloadManager.
    # These can be customized as desired, but the keys must not be changed
    optionDict: dict = \
    {
        'URL': "https://youtu.be/dQw4w9WgXcQ",  # Enter the URL for the medium to be downloaded here
        'PATH': r"C:\Users\Public\8kdownload",  # Enter the path here where the downloaded files should be saved
        'FORMAT': 'mp4',  # Whether the final file should be MP3 or MP4. (Only taken with POSTPROCESS=True)
        'FLAG': 'video',  # Whether the video or playlist should be downloaded (link with a video and playlist ID)
        'QUAL': (320, (320, 4320)),  # The quality in kBit/s and picture height: (Audio, (Audio, Video))
        'POSTPROCESS': True,  # Whether the files should be merged after the download (recommended)
        'THUMBNAIL': True,  # Whether a thumbnail should be downloaded and added
        'SUBTITLES': True,  # Whether subtitles should be downloaded (YouTube only)
        'TIMEOUT': 1,  # Seconds to wait after each download. Helps with rate limiting problems
        'SILENT_OUTPUT': False,  # Whether the output should be silent
        'USE_JSON': False,  # This option allows to specify multiple links in a JSON file
        'JSON_PATH': r"C:\Users\Public\links.json"  # Path to the JSON file if USE_JSON is used else None
    }

    async def main():  # asynchronous function that starts the download
        download: DownloadManager = DownloadManager()  # Create an instance of the DownloadManager
        await download.setOptions(optionDict)  # Set the options defined above for the download
        await download.downloadVideo()  # Downloads the medium specified in the URL with the set options

    start: float = time()  # Time at the beginning of the download

    try:
        if input("Want to start Download? (y/n) ").lower() == 'y':
            run(main())  # The asynchronous function is called
            print(f"Download completed in {time() - start:.2f} seconds.")  # Output of the elapsed time in seconds

        else:
            print("Bye! 👋")

    except Exception as ERR_04:
        print(f"An error occurred: {ERR_04}")  # Output error message if an exception occurs
