# 8K Video Downloader - Version 8.0

## About the Project

The 8K Video Downloader is a powerful tool for downloading video and audio files from various platforms in different resolutions, including up to 8K. This version offers a complete overhaul of the code and the addition of new features. Note that this program currently only works on Windows.

## Features

- **Supported Platforms**: YouTube, Twitch, SoundCloud & Podcast.de
- **Resolutions**: Download videos in up to 8K resolution
- **Thumbnails**: Download and add thumbnails
- **Subtitles**: Download and add subtitles
- **Formats**: Support for MP3 and MP4 downloads
- **Playlist Downloads**: Support for playlist downloads
- **User Interface**: Modern GUI with CustomTkinter
- **Advanced Options**: Accessible via the `CTRL + O` keyboard shortcut
- **Multiple Downloads**: As many downloads as desired via JSON file

## Requirements

- `Python 3.8 or higher` (tested with Python 3.12)
- `FFmpeg`
- `yt_dlp`
- `Pillow`
- `customtkinter`
- `CTkMessagebox`
- `beautifulsoup4`
- `requests`
- `vlc`

Additionally, several Python standard libraries are used, which do not require separate installation:

- `winreg`
- `os`
- `subprocess`
- `re`
- `logging`
- `time`
- `tkinter`
- `sys`
- `typing`
- `datetime`
- `asyncio`
- `collections`
- `json`

## Setting up the Environment

1. **Check Python Version**:
    ```bash
    python --version
    ```
    If the version is not `Python 3.8` or higher, download and install the latest version of Python [here](https://www.python.org/downloads/). Ensure that Python is added to the PATH.

2. **Install Required Packages**:
    ```bash
    pip install yt_dlp Pillow customtkinter CTkMessagebox beautifulsoup4 requests python-vlc
    ```

3. **Download Directory from GitHub**:
    Click on [this link](https://download-directory.github.io/?url=https://github.com/Lukasxlama/8K-YouTube-Downloader/tree/main/Version%208.0) to download the directory and extract it to any folder.

4. **Install FFmpeg**:
    Go to the following [section](#installation---ffmpeg) for detailed instructions on installing FFmpeg.

5. <a id="step-5"></a> **Run the Program**:
    Navigate to the directory where the `__main__.py` file is located and execute the following command:
    ```bash
    python .\__main__.py
    ```
    If everything works, you can take a look at the [supported formats](#supported-formats).
    If no GUI appears, check the logs in the `\logs` directory for error messages.

## Installation - FFmpeg

1. **Download FFmpeg Binaries**:
    Download the `FFmpeg` binaries from the official website [ffmpeg.org](https://ffmpeg.org/download.html) or use [this shortcut](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z).

2. **Create Directory Structure**:
    Extract the downloaded archive into the program directory. The structure should look like this:
    ```
    8K_Video_Downloader/
    ├── ffmpeg/
    │   └── bin/
    │       ├── ffmpeg.exe
    │       └── ffprobe.exe
    │       ...
    ├── logs/
    │   └── ...
    ├── media/
    │   └── ...
    ├── themes/
    │   └── ...
    ├── __main__.py
    ├── DependenciesManager.py
    ├── DownloadManager.py
    ├── downloads.json
    ├── GUIManager.py
    ├── JSONManager.py
    ├── LinkManager.py
    ├── LoggingManager.py
    ├── MessageBoxManager.py
    ├── OutputStreamHandler.py
    ├── PostprocessorManager.py
    ```

Now you can proceed with [Step 5](#step-5).

## Supported Formats

| Platform       | Type                  | MP3  | MP4  | Subtitles | Thumbnail |
|----------------|-----------------------|------|------|-----------|-----------|
| **YouTube**    | Video                 | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Playlist              | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Shorts                | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Shorts Shortlink      | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Video Shortlink       | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | User                  | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Channel               | ✅   | ✅   | ✅        | ✅        |
| **YouTube**    | Embedded              | ✅   | ✅   | ✅        | ✅        |
| **Twitch**     | VOD                   | ✅   | ✅   | ❌        | ✅        |
| **Twitch**     | Clip                  | ✅   | ✅   | ❌        | ✅        |
| **SoundCloud** | Track                 | ✅   | ❌   | ❌        | ✅        |
| **SoundCloud** | Playlist              | ✅   | ❌   | ❌        | ✅        |
| **Podcast.de** | Episode               | ✅   | ❌   | ❌        | ✅        |
| **Podcast.de** | Podcast               | ✅   | ❌   | ❌        | ✅        |

## Official Websites and Documentation

Here are the links to the tools used in this project:

- `FFmpeg`: [Website](https://ffmpeg.org/)
- `yt_dlp`: [GitHub Repository](https://github.com/yt-dlp/yt-dlp)
- `CustomTkinter`: [GitHub Repository](https://github.com/TomSchimansky/CustomTkinter)
- `CTkMessageBox`: [GitHub Repository](https://github.com/Akascape/CTkMessagebox)
- `BeautifulSoup4`: [GitHub Repository](https://github.com/wention/BeautifulSoup4)
- `Pillow`: [GitHub Repository](https://github.com/python-pillow/Pillow)
- `requests`: [GitHub Repository](https://github.com/psf/requests)
- `vlc`: [GitHub Repository](https://github.com/oaubert/python-vlc/tree/master)
