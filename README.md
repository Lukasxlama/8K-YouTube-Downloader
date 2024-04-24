# 8K YouTube Downloader - Version 7.0

## About the Project

The 8K YouTube Downloader is a handy tool for downloading YouTube videos in various resolutions, including up to 8K. This version offers a complete overhaul of the code and the addition of new features, such as automatic thumbnail embedding in MP3 and MP4 files.

## Features

- Download videos in up to 8K resolution
- Playlist download support
- Support for MP3 and MP4 downloads
- Modern user interface with CustomTkinter (CTk)
- Advanced error handling and logging

## Requirements

- Python 3.8 or higher
- FFMPEG
- `yt_dlp`: A library for downloading videos and playlists from YouTube.
- `Pillow`: An image processing library used as a successor to PIL (Python Imaging Library).
- `customtkinter`: An enhanced version of Tkinter that offers improved and more modern UI components.
- `CTkMessagebox`: An enhanced MessageBox widget that uses CustomTkinter.

Additionally, several standard Python libraries are used which are provided with the Python installation and do not require separate installation:

- `winreg` (only available on Windows systems)
- `os`
- `concurrent.futures`
- `subprocess`
- `re`
- `logging`
- `time`
- `tkinter`

## Installing Dependencies

To install the required Python packages, use the following command:

```bash
pip install yt_dlp Pillow customtkinter CTkMessagebox
```

## Installation - FFMPEG
To install `FFMPEG`, please follow these steps:
1. Download the `FFMPEG` binarys from the official website [ffmpeg.org](https://ffmpeg.org/download.html) or use this [shortcut](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)
2. Extract the downloaded archive into the folder where your program is located. The structure should look like this:

    ```
    8K_YouTube_Downloader/
    ├── ffmpeg/
    │   └── bin/
    │       ├── ffmpeg.exe
    │       └── ffprobe.exe
    │       ...
    │
    ├── __main__.py
    ├── Dependencies.py
    ├── DownloadVideo.py
    ├── ExtractVideoID.py
    ├── LoggerConfig.py
    ├── MessageBoxes.py
    │   ...
    ```

    The path `{path.dirname(path.abspath(__file__))}\ffmpeg\bin` is crucial for the program's functionality. If FFMPEG is not found in this directory, the program will terminate with a log.critical error message.

3. Ensure that you adjust the path specifications in `DownloadVideo.py` if you wish to use a different structure. The program expects the `ffmpeg.exe` and `ffprobe.exe` files to be in the specified `ffmpeg\bin` directory.

## Official Websites and Documentation
- `yt_dlp`: [GitHub Repository of yt-dlp](https://github.com/yt-dlp/yt-dlp)
- `CustomTkinter`: [GitHub Repository of CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- `CTkMessageBox`: [GitHub Repository of CTkMessageBox](https://github.com/Akascape/CTkMessagebox)
