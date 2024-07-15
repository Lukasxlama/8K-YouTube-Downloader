######################################
# Projekt: 8K Video Downloader       #
# Dateiname: PostprocessorManager.py #
# Version: 8.0                       #
# Autor: lukasxlama                  #
######################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Other #
    from subprocess import run, CalledProcessError, PIPE, CompletedProcess
    from typing import List, Dict, Optional, Union, Tuple, Any
    from os import path, listdir, rename, remove
    from asyncio import to_thread, gather
    from collections import defaultdict
    from threading import Lock
    from re import search, sub
    from PIL import Image

    import sys

except ImportError as ERR_01:
    print(f"[PostprocessorManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class PostprocessorManagerBase:
    """
    A base class for managing post-processing tasks using FFmpeg.

    This class provides methods for setting options, running FFmpeg commands,
    and processing media files such as adding thumbnails, converting formats,
    and handling downloaded files.
    """

    def __init__(self) -> None:
        """
        Initializes the PostprocessorManagerBase class.

        :return: None.
        :raises SystemExit: If FFmpeg is not found at the specified path.
        """

        self.ffmpegPath: str = path.join(path.dirname(path.abspath(__file__)), 'ffmpeg', 'bin', 'ffmpeg.exe')
        if not path.exists(self.ffmpegPath):
            log.error(f"[PostprocessorManager.py@__init__] FFmpeg not found at {self.ffmpegPath}")
            raise SystemExit(-810)

        self.options: Optional[Dict[str, Any]] = None
        self.lock: Lock = Lock()

    def setOptions(self, OPT_DICT: Dict[str, Any]) -> None:
        """
        Sets the options for the PostprocessorManagerBlueprint.

        :param OPT_DICT: A dictionary containing the options for the postprocessor.
        :return: None.
        """

        for key in ['PATH', 'FORMAT', 'QUAL']:
            if key not in OPT_DICT:
                raise ValueError(f"[PostprocessorManager.py@setOptions] Missing required option: {key}")

        self.options = OPT_DICT

    @staticmethod
    def runCommand(CMD: List[str]) -> None:
        """
        Workaround for asynchronous subprocess.run() to redirect the streams.

        :return: None.
        """

        result: CompletedProcess[str] = run(CMD, check=True, stdout=PIPE, stderr=PIPE, text=True)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)

    async def collectDownloadedFiles(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Collects the downloaded files from the specified path and creates a dictionary.

        :return: Dictionary with paths of downloaded files, containing 'media', 'thumbnail', and 'subtitle' keys.
        """

        raise NotImplementedError("This method should be implemented by subclasses.")

    async def addThumbnailToMP3(self, MP3: str, PNG: str) -> None:
        """
        Adds a thumbnail to an MP3 file using FFmpeg.

        :param MP3: Path to the MP3 file.
        :param PNG: Path to the PNG file.
        :return: None.
        """

        cmd: List[str] = [self.ffmpegPath, '-y', '-i', MP3, '-i', PNG, '-map', '0:a', '-map', '1', '-c:a', 'copy',
                          '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v',
                          'comment="Cover (front)"', path.splitext(MP3)[0] + '.final.mp3']

        try:
            log.info(f"[PostprocessorManager.py@addThumbnailToMP3] FFmpeg Command: {' '.join(cmd)}")
            await to_thread(self.runCommand, cmd)
            await to_thread(remove, MP3)
            await to_thread(remove, PNG)
            await to_thread(rename, path.splitext(MP3)[0] + '.final.mp3', MP3)
            log.info(f"[PostprocessorManager.py@addThumbnailToMP3] Successfully added thumbnail to {MP3}")

        except CalledProcessError as ERR_02:
            log.error("[PostprocessorManager.py@addThumbnailToMP3] "
                      f"Error adding thumbnail to {MP3}: {ERR_02}", exc_info=True)

    async def convertAnyToMP3(self, PATH: str) -> str:
        """
        Converts any audio or video file to an MP3 file.

        :param PATH: Path to the audio or video file.
        :return: Path to the new MP3 file.
        """

        if not await to_thread(path.exists, PATH):
            log.error(f"[PostprocessorManager.py@convertAnyToMP3] Audio file does not exist: {PATH}")
            return None

        elif path.splitext(PATH)[1].lower() == '.mp3':
            return PATH

        mp3_path: str = path.splitext(PATH)[0] + '.mp3'
        cmd: List[str] = [self.ffmpegPath, '-y', '-i', PATH, '-c:a', 'libmp3lame', '-b:a',
                          f'{self.options.get("QUAL", [128])[0]}k', mp3_path]

        try:
            log.info(f"[PostprocessorManager.py@convertAnyToMP3] FFmpeg Command: {' '.join(cmd)}")
            await to_thread(self.runCommand, cmd)
            await to_thread(remove, PATH)
            log.info(f"[PostprocessorManager.py@convertAnyToMP3] Successfully converted {PATH} to {mp3_path}")
            return mp3_path

        except CalledProcessError as ERR_03:
            log.error("[PostprocessorManager.py@convertAnyToMP3] "
                      f"Error converting {PATH} to MP3: {ERR_03}", exc_info=True)
            return PATH

    @staticmethod
    async def convertAnyToPNG(PATH: str) -> str:
        """
        Converts any image file to an PNG file.

        :param PATH: Path to the image file.
        :return: Path to the new PNG file.
        """

        if not await to_thread(path.exists, PATH):
            log.error(f"[PostprocessorManager.py@convertAnyToPNG] Image file does not exist: {PATH}")
            return None

        elif path.splitext(PATH)[1].lower() == '.png':
            return PATH

        try:
            with Image.open(PATH) as img:
                await to_thread(img.save, path.splitext(PATH)[0] + '.png', 'PNG')

            await to_thread(remove, PATH)
            log.info("[PostprocessorManager.py@convertAnyToPNG] Successfully converted "
                     f"{PATH} to {path.splitext(PATH)[0] + '.png'}")
            return path.splitext(PATH)[0] + '.png'

        except Exception as ERR_04:
            log.error("[PostprocessorManager.py@convertAnyToPNG] "
                      f"Error converting {PATH} to PNG: {ERR_04}", exc_info=True)
            return PATH

    async def processFile(self, *ARGS) -> str:
        """
        Converts media files, optionally adds thumbnails and subtitles using FFmpeg.

        :param ARGS: Arguments required for processing the file.
        :return: Path to the processed file.
        """

        raise NotImplementedError("This method should be implemented by subclasses.")

    def getProcessFileArgs(self, PATHS: Dict[str, Optional[Union[str, List[str]]]]) -> Tuple[str]:
        """
        Returns the arguments required for the processFile method.

        :param PATHS: A dictionary containing paths for media, thumbnail, and optionally subtitles.
        :return: A tuple of arguments for the processFile method.
        """

        raise NotImplementedError("This method should be implemented by subclasses.")

    def getNewMediaPath(self, MEDIA_PATH: str) -> str:
        """
        Returns the new media path after renaming.

        :param MEDIA_PATH: The original media path.
        :return: The new media path after renaming.
        """

        raise NotImplementedError("This method should be implemented by subclasses.")

    async def processFiles(self) -> None:
        """
        Applies the respective postprocessor routine to the path specified in the options

        :return: None.
        """

        if not self.options:
            log.critical("[PostprocessorManagerBase@processFiles] Options have not been set.")
            return

        downloaded_files: Dict[str, Dict[str, Optional[str]]] = await self.collectDownloadedFiles()
        log.info(f"[PostprocessorManager.py@processFiles] {downloaded_files}")

        new_media_paths: Tuple[str] = await gather(
            *(
                self.processFile(*self.getProcessFileArgs(paths))
                for title, paths in downloaded_files.items()
            )
        )

        for _, new_media_path in zip(downloaded_files.items(), new_media_paths):
            if new_media_path and new_media_path != (final_media_path := self.getNewMediaPath(new_media_path)):
                try:
                    with self.lock:
                        if path.exists(final_media_path):
                            log.warning(f"[PostprocessorManager.py@processFiles] File {final_media_path} already "
                                        "exists. Overwriting it.")
                            await to_thread(remove, final_media_path)
                        await to_thread(rename, new_media_path, final_media_path)

                    log.info(f"[PostprocessorManager.py@processFiles] Renamed {new_media_path} to {final_media_path}")

                except PermissionError as ERR_05:
                    log.error("[PostprocessorManager.py@processFiles] Permission error while renaming "
                              f"{new_media_path} to {final_media_path}: {ERR_05}")

                except Exception as ERR_06:
                    log.error("[PostprocessorManager.py@processFiles] Error while renaming "
                              f"{new_media_path} to {final_media_path}: {ERR_06}")

class YouTubePostprocessorManager(PostprocessorManagerBase):
    """
    A class that manages post-processing tasks for YouTube downloads.
    """

    def __init__(self) -> None:
        """
        Calles the constructor of PostprocessorManagerBase.

        :return: None.
        """

        super().__init__()

    async def collectDownloadedFiles(self):
        if not await to_thread(path.isdir, self.options.get('PATH')):
            raise ValueError("The specified PATH is not a valid directory.")

        files: defaultdict[str, Dict[str, Optional[Union[str, List[str]]]]] = defaultdict(lambda: {
            'media': None, 'thumbnail': None, 'subtitles': []})

        for file in await to_thread(listdir, self.options.get('PATH')):
            full_path: str = path.join(self.options.get('PATH'), file)

            if any(file.endswith(ext) for ext in [".8kdownload.webm", ".8kdownload.mp4", ".8kdownload.m4a",
                                                  ".8kdownload.mp3"]):
                title: str = sub(r'\.8kdownload\.(webm|mp4|m4a|mp3)$', '', file)
                files[title]['media'] = full_path

            elif any(file.endswith(ext) for ext in [".8kdownload.webp", ".8kdownload.jpg", ".8kdownload.jpeg",
                                                    ".8kdownload.png"]):
                title: str = sub(r'\.8kdownload\.(webp|jpg|jpeg|png)$', '', file)
                files[title]['thumbnail'] = full_path

            elif search(r"\.8kdownload\.[A-Za-z0-9-]+\.vtt$", file):
                files[sub(r'\.8kdownload\.[A-Za-z0-9-]+\.vtt$', '', file)]['subtitles'].append(full_path)

        return {key: value for key, value in files.items() if value['media']}

    def getProcessFileArgs(self, PATHS):
        return PATHS.get('media', ''), PATHS.get('subtitles', []), PATHS.get('thumbnail', '')

    def getNewMediaPath(self, MEDIA_PATH):
        return path.join(self.options.get('PATH'), path.splitext(path.basename(MEDIA_PATH))[0] +
                         f".{self.options.get('FORMAT')}").replace('.8kdownload', '')

    async def processFile(self, MEDIA_PATH: str, SUBTITLES: List[str], THUMB: Optional[str]):
        if self.options.get('FORMAT') not in ['mp4', 'mp3']:
            log.error(f"[PostprocessorManager.py@processFile] Unsupported output format: {self.options.get('FORMAT')}")
            return

        log.debug(f"[PostprocessorManager.py@processFile] Processing {MEDIA_PATH}, {SUBTITLES}, {THUMB}")

        new_path: str = MEDIA_PATH if MEDIA_PATH.endswith(f'.{self.options.get("FORMAT")}') else (
            path.join(self.options.get('PATH'), path.splitext(path.basename(MEDIA_PATH))[0] +
                      f'.{self.options.get('FORMAT')}'))
        new_path = new_path.replace('.8kdownload', '')
        png_thumb: Optional[str] = None

        if THUMB:
            png_thumb = await self.convertAnyToPNG(THUMB)

        cmd: List[str] = [self.ffmpegPath, '-y', '-i', MEDIA_PATH]

        if png_thumb:
            cmd.extend(['-i', png_thumb])

        if self.options.get('FORMAT') == 'mp4':
            for subtitle in SUBTITLES:
                cmd.extend(['-i', subtitle])

            cmd.extend(['-map', '0:v', '-map', '0:a'])

            for i in range(len(SUBTITLES)):
                cmd.extend(['-map', f'{i + 1}', '-c:s', 'mov_text'])

            if png_thumb:
                cmd.extend(['-map', f'{len(SUBTITLES) + 1}', '-c:v', 'copy', '-c:a', 'aac', '-disposition:v:1',
                            'attached_pic'])

            else:
                cmd.extend(['-c:v', 'copy', '-c:a', 'aac'])

        elif self.options.get('FORMAT') == 'mp3':
            cmd.extend(['-map', '0:a'])

            if png_thumb:
                cmd.extend(['-map', '1', '-c:a', 'libmp3lame', '-b:a', f'{self.options.get("QUAL",
                            (320, (320, 4320)))[1][0]}k', '-id3v2_version', '3', '-metadata:s:v',
                            'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"'])

            else:
                cmd.extend(['-c:a', 'libmp3lame', '-b:a', f'{self.options.get("QUAL", (320, (320, 4320)))[1][0]}k',
                            '-id3v2_version', '3'])

        cmd.append(new_path)

        try:
            log.info(f"[PostprocessorManager.py@processFile] FFmpeg Command: {' '.join(cmd)}")
            await to_thread(self.runCommand, cmd)

            await to_thread(remove, MEDIA_PATH)

            if png_thumb:
                await to_thread(remove, png_thumb)

            for subtitle in SUBTITLES:
                await to_thread(remove, subtitle)

            log.info("[PostprocessorManager.py@processFile] "
                     f"Successfully processed {MEDIA_PATH} to {new_path}")

            return new_path

        except CalledProcessError as ERR_07:
            log.error("[PostprocessorManager.py@processFile] "
                      f"Error processing {MEDIA_PATH} to {self.options.get('FORMAT').upper()}: {ERR_07}", exc_info=True)

    async def processFiles(self):
        await super().processFiles()

        if not self.options.get('THUMBNAIL') and not self.options.get('LINK_TYPE') in ['playlist', 'user']:
            return

        playlistUsername: str = self.options.get('PLAYLIST_USER_NAME', None)

        if playlistUsername:
            for file in listdir(self.options.get('PATH')):
                if file.startswith(playlistUsername) and file.endswith(('.jpg', '.png', '.webp')):
                    remove(path.join(self.options.get('PATH'), file))
                    log.info(f"[PostprocessorManager.py@processFile] Removed playlist thumbnail: {file}")
                    break

        else:
            log.info("[PostprocessorManager.py@processFile] The playlist/username from the DownloadManager is missing, "
                     "skip deleting the thumbnail")

class TwitchPostprocessorManager(PostprocessorManagerBase):
    """
    A class that manages post-processing tasks for Twitch downloads.
    """

    def __init__(self) -> None:
        """
        Calles the constructor of PostprocessorManagerBase.

        :return: None.
        """

        super().__init__()

    async def collectDownloadedFiles(self):
        if not await to_thread(path.isdir, self.options.get('PATH')):
            raise ValueError("The specified PATH is not a valid directory.")

        files: defaultdict[str, Dict[str, Optional[Union[str, List[str]]]]] = defaultdict(lambda: {'media': None,
                                                                                                   'thumbnail': None})

        for file in await to_thread(listdir, self.options.get('PATH')):
            full_path: str = path.join(self.options.get('PATH'), file)

            if file.endswith(".8kdownload.mp4"):
                title: str = file.replace('.8kdownload.mp4', '')
                files[title]['media'] = full_path

            elif file.endswith(".8kdownload.jpg"):
                title: str = file.replace('.8kdownload.jpg', '')
                files[title]['thumbnail'] = full_path

        return dict(files)

    def getProcessFileArgs(self, PATHS):
        return PATHS.get('media', ''), PATHS.get('thumbnail', '')

    def getNewMediaPath(self, MEDIA_PATH):
        return MEDIA_PATH.replace('.8kdownload', '')

    async def processFile(self, MEDIA_PATH: str, THUMB: Optional[str]) -> None:
        if self.options.get('FORMAT') not in ['mp4', 'mp3']:
            log.error("[PostprocessorManager.py@processFile] "
                      f"Unsupported output format: {self.options.get('FORMAT')}")
            return

        new_path: str = path.join(self.options.get('PATH'), path.splitext(path.basename(MEDIA_PATH))[0] +
                                  f'.converted.{self.options.get('FORMAT')}')
        final_path: str = path.join(self.options.get('PATH'), path.splitext(path.basename(MEDIA_PATH))[0] +
                                    f'.{self.options.get('FORMAT')}')
        png_thumb: Optional[str] = None

        if THUMB:
            png_thumb = await self.convertAnyToPNG(THUMB)

        cmd: List[str] = [self.ffmpegPath, '-y', '-i', MEDIA_PATH]

        if png_thumb:
            cmd.extend(['-i', png_thumb])

        if self.options.get('FORMAT') == 'mp4':
            cmd.extend(['-map', '0:v', '-map', '0:a'])

            if png_thumb:
                cmd.extend(['-map', '1', '-c:v', 'copy', '-c:a', 'copy', '-disposition:v:1', 'attached_pic'])
            else:
                cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])

        elif self.options.get('FORMAT') == 'mp3':
            cmd.extend(['-map', '0:a'])

            if png_thumb:
                cmd.extend(['-map', '1', '-c:a', 'libmp3lame', '-b:a', f'{self.options.get("QUAL", [128])[0]}k',
                            '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"', '-metadata:s:v',
                            'comment="Cover (front)"'])
            else:
                cmd.extend(['-c:a', 'libmp3lame', '-b:a', f'{self.options.get("QUAL", [128])[0]}k',
                            '-id3v2_version', '3'])

        cmd.append(new_path)

        try:
            log.info(f"[PostprocessorManager.py@processFile] FFmpeg Command: {' '.join(cmd)}")
            await to_thread(self.runCommand, cmd)
            await to_thread(remove, MEDIA_PATH)

            if png_thumb:
                await to_thread(remove, png_thumb)

            if await to_thread(path.exists, final_path):
                await to_thread(remove, final_path)
            await to_thread(rename, new_path, final_path)

            log.info("[PostprocessorManager.py@processFile] "
                     f"Successfully processed {MEDIA_PATH} to {final_path}")
            print(f"\n\n\n{new_path}\n{final_path}\n\n\n")
            return final_path

        except CalledProcessError as ERR_08:
            log.error("[PostprocessorManager.py@processFile] "
                      f"Error processing {MEDIA_PATH} to {self.options.get('FORMAT').upper()}: {ERR_08}", exc_info=True)

class SoundcloudPostprocessorManager(PostprocessorManagerBase):
    """
    A class that manages post-processing tasks for SoundCloud downloads.
    """

    def __init__(self) -> None:
        """
        Calles the constructor of PostprocessorManagerBase.

        :return: None.
        """

        super().__init__()

    async def collectDownloadedFiles(self):
        if not await to_thread(path.isdir, self.options.get('PATH')):
            raise ValueError("The specified PATH is not a valid directory.")

        files: defaultdict[str, Dict[str, Optional[str]]] = defaultdict(lambda: {'media': None, 'thumbnail': None})

        for file in await to_thread(listdir, self.options.get('PATH')):
            full_path: str = path.join(self.options.get('PATH'), file)

            if file.endswith(".8kdownload.opus"):
                title: str = file.replace('.8kdownload.opus', '')
                files[title]['media'] = full_path

            elif file.endswith(".8kdownload.mp3"):
                title: str = file.replace('.8kdownload.mp3', '')
                files[title]['media'] = full_path

            elif file.endswith(".8kdownload.jpg"):
                title: str = file.replace('.8kdownload.jpg', '')
                files[title]['thumbnail'] = full_path
        print(dict(files))
        return dict(files)

    def getProcessFileArgs(self, PATHS):
        return PATHS.get('media', ''), PATHS.get('thumbnail', '')

    def getNewMediaPath(self, MEDIA_PATH):
        return MEDIA_PATH.replace('.8kdownload', '')

    async def processFile(self, MEDIA_PATH: str, THUMB: Optional[str]) -> None:
        if THUMB:
            await self.addThumbnailToMP3(new_path := await self.convertAnyToMP3(MEDIA_PATH),
                                         await self.convertAnyToPNG(THUMB))
            return new_path

        else:
            return await self.convertAnyToMP3(MEDIA_PATH)

class PodcastdePostprocessorManager(PostprocessorManagerBase):
    """
    A class that manages post-processing tasks for Podcast.de downloads.
    """

    def __init__(self) -> None:
        """
        Calles the constructor of PostprocessorManagerBase.

        :return: None.
        """

        super().__init__()

    async def collectDownloadedFiles(self):
        if not await to_thread(path.isdir, self.options.get('PATH')):
            raise ValueError("The specified PATH is not a valid directory.")

        files: defaultdict[str, Dict[str, Optional[str]]] = defaultdict(lambda: {'media': None, 'thumbnail': None})

        for file in await to_thread(listdir, self.options.get('PATH')):
            full_path: str = path.join(self.options.get('PATH'), file)

            if file.endswith(".8kdownload.png"):
                title: str = file.replace('.8kdownload.png', '')
                files[title]['thumbnail'] = full_path

            elif file.endswith(".8kdownload.mp3") or file.endswith(".8kdownload.m4a") or\
                    file.endswith(".8kdownload.opus"):
                title: str = file.replace('.8kdownload.mp3', '').replace('.8kdownload.m4a', '').replace(
                    '.8kdownload.opus', '')
                files[title]['media'] = full_path

        return dict(files)

    def getProcessFileArgs(self, PATHS):
        return PATHS.get('media'), PATHS.get('thumbnail')

    def getNewMediaPath(self, MEDIA_PATH) :
        return sub(r' ~ .*?(\.[a-zA-Z0-9]+)$', r'\1', MEDIA_PATH)

    async def processFile(self, MEDIA_PATH: str, THUMB: Optional[str]):
        if THUMB:
            await self.addThumbnailToMP3(new_path := await self.convertAnyToMP3(MEDIA_PATH), THUMB)
            return new_path

        else:
            return await self.convertAnyToMP3(MEDIA_PATH)
