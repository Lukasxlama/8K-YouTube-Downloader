##################################
# Project: 8K Video Downloader   #
# Filename: LinkManager.py       #
# Version: 8.0                   #
# Author: lukasxlama             #
##################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Others ##
    from urllib.parse import urlparse, parse_qs, urlunparse, urlencode, ParseResult
    from typing import List, Dict, Tuple, Optional, Union
    from re import findall, search

except ImportError as ERR_01:
    print(f"[LinkManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class LinkManager:
    """
    Manages the extraction of IDs and other details from URLs based on specified patterns.
    """

    def __init__(self) -> None:
        """
        Initializes the LinkManager with specific URL patterns.

        Patterns can be added dynamically here to support specific URLs and therefore specific platforms.
        It should be noted that:
            - yt-dlp must support the platform/media.
            - getMediaInfo must be extended by an elif block
            - determineFormatSettings in DownloadManager.py must be extended by an elif block.
            - Postprocessing in PostprocessorManager.py must be updated.
            - Postprocessor must be added in DownloadManager + case block

        :return: None.
        """

        self.patterns: dict = \
        {
            ## YouTube ##
            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_VIDEO": r"[?&]v=([a-zA-Z0-9_-]{11})(?:&|$)",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_PLAYLIST": r"[?&]list=([a-zA-Z0-9_-]{34})(?:&|$)",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_SHORTS": r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_SHORTS_SHORTLINK": r"youtu\.be\/shorts\/([a-zA-Z0-9_-]{11})",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_VIDEO_SHORTLINK": r"youtu\.be/([a-zA-Z0-9_-]{11})",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_USER": r"youtube\.com/@([a-zA-Z0-9_]+)(?:/([a-zA-Z]+))?",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_CHANNEL": r"youtube\.com/channel/([a-zA-Z0-9_-]{24})(?:\?.*)?$",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ✅ / THUMBNAIL ✅ ) #
            "YOUTUBE_EMBEDDED": r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",

            ## Twitch ##
            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "TWITCH_VOD": r"twitch\.tv/videos/(\d+)",

            # Verified ( MP3 ✅ / MP4 ✅ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "TWITCH_CLIP": r"twitch\.tv/([^/]+)/clip/([a-zA-Z0-9_-]+)",

            ## SoundCloud ##
            # Verified ( MP3 ✅ / MP4 ❌ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "SOUNDCLOUD_TRACK": r"soundcloud\.com/[^/]+/(?!(tracks|popular-tracks|albums|sets|reposts)$)([^/?#&]+)$",

            # Verified ( MP3 ✅ / MP4 ❌ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "SOUNDCLOUD_PLAYLIST": r"soundcloud\.com/[^/]+/sets/([^/?#&]+)$",

            ## Podcast.de ##
            # Verified ( MP3 ✅ / MP4 ❌ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "PODCASTDE_EPISODE": r"podcast\.de/episode/\d+/.+",

            # Verified ( MP3 ✅ / MP4 ❌ / SUBTITLES ❌ / THUMBNAIL ✅ ) #
            "PODCASTDE_PODCAST": r"podcast\.de/podcast/\d+/archiv",
        }

    async def extractInfo(self, URL: str) -> Dict[str, str]:
        """
        Asynchronously extracts information from URLs using regular expressions defined in patterns.

        :param URL: The URL from which to extract information.
        :return: A dictionary containing all found data or an error message.
        """

        cleanURL: str = self.removeQueryParams(URL, KEEP_PARAMS=["v", "list"])

        results: Dict[str, str] = {}
        for key, pattern in self.patterns.items():
            matches: List[str] = findall(pattern, cleanURL)

            if matches:
                if "TWITCH_CLIP" in key and len(matches[0]) == 2:
                    results[key] = {"channel": matches[0][0], "clip_id": matches[0][1]}

                elif "SOUNDCLOUD" in key:
                    results[key] = {'username': matches[0][0], 'identifier': matches[0][1]} if len(
                        matches[0]) > 1 else {'username': matches[0][0]}

                else:
                    results[key] = matches[0] if len(matches) == 1 else matches

        if not results:
            log.error(f"[LinkManager.py@extractInfo] No data could be extracted from: {cleanURL}")
            return {"error": "No data could be extracted"}

        results['url'] = cleanURL
        return results

    @staticmethod
    def removeQueryParams(URL: str, KEEP_PARAMS: List[str] = None) -> str:
        """
        Removes query parameters from a URL except for specified parameters to keep.

        :param URL: The original URL.
        :param KEEP_PARAMS: List of query parameters to keep.
        :return: The URL without unnecessary query parameters.
        """

        if KEEP_PARAMS is None:
            KEEP_PARAMS = list()

        parsed: ParseResult = urlparse(URL)
        query_args: Dict[str, List[str]] = parse_qs(parsed.query)
        filtered_query: Dict[str, List[str]] = {k: v for k, v in query_args.items() if k in KEEP_PARAMS}
        query_string: str = urlencode(filtered_query, doseq=True)

        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, query_string, parsed.fragment))

    def isUrlValid(self, URL: str) -> Tuple[bool, Optional[str]]:
        """
        Validates a URL based on predefined patterns to check if it matches any known service format and identifies
        the platform.

        :param URL: The URL to validate.
        :return: Tuple where bool indicates if the URL is valid and str indicates the platform or None if invalid.
        """

        if not URL:
            return False, None

        parsedURL: ParseResult = urlparse(URL)

        if not parsedURL.scheme or not parsedURL.netloc:
            return False, None

        for key, pattern in self.patterns.items():
            if search(pattern, URL):
                return True, key.split('_')[0].lower()

        return False, None

    async def getMediaInfo(self, URL: str) -> Dict[str, Union[str, bool]]:
        """
        Wrapper for extractInfo to parse URLs and return structured media information.

        :param URL: The URL to analyze.
        :return: Dictionary with success status, media type, media ID, platform, and an error message if applicable.
        """

        info: Dict[str, str] = await self.extractInfo(URL)

        if not info:
            return {'LINK_SUCCESS': False, 'LINK_ERROR': 'No data could be extracted!'}

        for key in info.keys():
            platform: str = key.split("_")[0].lower()
            media_type: str = key.split("_")[1].lower()

            if 'YOUTUBE' in key:
                return {'LINK_SUCCESS': True, 'LINK_URL': info.get('url'), 'LINK_PLATFORM': platform,
                        'LINK_TYPE': media_type}

            elif 'TWITCH' in key:
                media_type = 'clip' if 'clip' in key else 'vod'
                return {'LINK_SUCCESS': True, 'LINK_URL': info.get('url'), 'LINK_PLATFORM': platform,
                        'LINK_TYPE': media_type}

            elif 'SOUNDCLOUD' in key:
                return {'LINK_SUCCESS': True, 'LINK_URL': info.get('url'), 'LINK_PLATFORM': platform,
                        'LINK_TYPE': media_type}

            elif 'PODCASTDE' in key:
                return {'LINK_SUCCESS': True, 'LINK_URL': info.get('url'), 'LINK_PLATFORM': platform,
                        'LINK_TYPE': media_type}

            # Add handling for other platforms here!

        return {'LINK_SUCCESS': False, 'LINK_ERROR': 'Unsupported URL type!'}
