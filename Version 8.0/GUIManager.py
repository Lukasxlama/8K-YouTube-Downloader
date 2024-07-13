##################################
# Projekt: 8K Video Downloader   #
# Dateiname: GUIManager.py       #
# Version: 8.0                   #
# Autor: lukasxlama              #
##################################

### Imports ###
try:
    ## Logging ##
    from LoggingManager import LoggingManager
    from logging import Logger

    ## Custom Modules ##
    from OutputStreamHandler import OutputHandler, StreamHandler
    from LinkManager import LinkManager
    from DownloadManager import DownloadManager
    from MessageBoxManager import MessageBoxManager

    ### Others ###
    from customtkinter import (CTk, CTkButton, CTkCheckBox, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu, END,
                               CTkToplevel, CTkProgressBar, CTkTextbox, CTkScrollableFrame, IntVar, StringVar,
                               set_appearance_mode, set_default_color_theme, CTkImage)
    from asyncio import new_event_loop, set_event_loop, get_event_loop, AbstractEventLoop
    from tkinter.filedialog import askdirectory, askopenfile
    from typing import Optional, Any, List, Dict
    from tkinter import Widget, TclError
    from threading import Thread
    from vlc import MediaPlayer
    from subprocess import run
    from tkinter import Event
    from re import search
    from PIL import Image
    from time import time
    from os import path

except ImportError as ERR_01:
    print(f"[GUIManager.py] Error during import: {ERR_01}")
    raise SystemExit(-810)

### Initialize Logger ###
LoggingManager()
log: Logger = LoggingManager.getLogger()

### Classes ###
class ToolTip:
    """
    A simple class to create and manage tooltips for Tkinter widgets.
    """

    def __init__(self, WIDGET: Widget, TEXT: str, PARENT_WINDOW: CTkToplevel) -> None:
        """
        Initializes the ToolTip class.

        :param WIDGET: The widget to which the tooltip is attached.
        :param TEXT: The text to display in the tooltip.
        :param PARENT_WINDOW: The parent window to manage topmost attribute.

        :return: None.
        """

        self.widget: Widget = WIDGET
        self.text: str = TEXT
        self.tipwindow: Optional[CTkToplevel] = None
        self.id: Optional[int] = None
        self.x: int = 0
        self.y: int = 0
        self.parentWindow: CTkToplevel = PARENT_WINDOW
        self.wasTopmost: bool = False
        self.widget.bind("<Enter>", lambda _EVENT: (self.unschedule(),
                                                    setattr(self, 'id', self.widget.after(450, self.showTip))))
        self.widget.bind("<Leave>", self.hideTip)

    def unschedule(self) -> None:
        """
        Cancels the scheduled tooltip display.

        :return: None.
        """

        tooltip_id = self.id
        self.id = None

        if tooltip_id:
            self.widget.after_cancel(tooltip_id)

    def showTip(self, _EVENT: Optional[Event] = None) -> None:
        """
        Displays the tooltip.

        :param _EVENT: The triggering event (unused).
        :return: None.
        """

        if self.tipwindow or not self.text:
            return

        self.wasTopmost = bool(self.parentWindow.attributes('-topmost'))

        if self.wasTopmost:
            self.parentWindow.attributes('-topmost', 0)

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = CTkToplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = CTkLabel(tw, text=self.text, justify='left', bg_color="#1D1E1E",
                         text_color="white", corner_radius=5, padx=5, pady=5)
        label.pack()

    def hideTip(self, _EVENT: Optional[Event] = None) -> None:
        """
        Hides the tooltip.

        :param _EVENT: The triggering event (unused).
        :return: None.
        """

        self.unschedule()
        tw = self.tipwindow
        self.tipwindow = None

        if tw:
            tw.destroy()

        if self.wasTopmost:
            self.parentWindow.attributes('-topmost', 1)

class GUIManager:
    """
    Manages the GUI for the 8K Video Downloader application.

    This class initializes the GUI, sets up the logger, managers, main window, and variables,
    and handles user interactions and download processes.
    """

    def __init__(self) -> None:
        """
        Initializes the GUIManager class, sets up the logger, managers, main window, and variables,
        and calls the setupGui method to initialize the GUI components.

        :return: None.
        """

        ## Get Manager Instances ##
        self.messageBoxManager: MessageBoxManager = MessageBoxManager()
        self.linkManager: LinkManager = LinkManager()
        self.downloadManager: DownloadManager = DownloadManager()

        ## Tkinter Main Window ##
        self.root: Optional[CTk] = None
        self.openWindows: Dict[str, CTkToplevel] = {}

        ## Variables ##
        self.optionInstallPacks: Optional[IntVar] = None
        self.optionMp3: Optional[IntVar] = None
        self.optionMp4: Optional[IntVar] = None
        self.scrollableRoot: Optional[CTkScrollableFrame] = None
        self.tooltips: Dict[str, str] = \
        {
            # URL Frame
            "urlEntry": "Input field for the URL. Permitted platforms are YouTube, Twitch, SoundCloud & Podcast.de.",
            "playlistButton": "Button to select playlist download mode.",
            "videoButton": "Button to select video download mode.",
            "urlIconLabel": "Indicator for URL validity.",

            # Quality Frame
            "mp3Button": "Checkbox to select MP3 download format.",
            "mp4Button": "Checkbox to select MP4 download format.",

            # Path Frame
            "outputEntry": "Input field for the output path.",
            "outputButton": "Button to browse for the output path.",
            "downloadButton": "Button to start the download process.",

            # Output Frame
            "consoleText": "Text area displaying download logs and messages.",
            "progressBar": "Progress bar showing the download progress.",
            "progressLabel": "Label displaying the download progress percentage.",

            # Advanced Options
            "postprocess_check": "Checkbox to enable post-processing of downloaded files.",
            "thumbnail_check": "Checkbox to download and add thumbnails to the media.",
            "subtitles_check": "Checkbox to download and add subtitles to the media.",
            "timeout_entry": "Input field for setting the timeout duration between downloads.",
            "sound_check": "Checkbox to enable sound notification after download.",
            "shutdown_check": "Checkbox to enable pc shutdown after download.",
            "json_output_check": "Checkbox that indicates whether a JSON file should be used for download settings.",
            "json_entry": "Input field for the path to the JSON file containing download settings.",
            "json_browse_button": "Button to browse and select the JSON file containing download settings.",
            "okay_button": "Button to apply advanced options changes and close the window."
        }

        ## URL Frame ##
        self.urlFrame: Optional[CTkFrame] = None
        self.optionUrl: Optional[StringVar] = None
        self.urlEntry: Optional[CTkEntry] = None
        self.urlIconLabel: Optional[CTkLabel] = None
        self.urlButtonVar: Optional[StringVar] = None
        self.playlistButton: Optional[CTkButton] = None
        self.videoButton: Optional[CTkButton] = None
        self.validUrlIcon: Optional[CTkImage] = None
        self.invalidUrlIcon: Optional[CTkImage] = None

        ## Quality Frame ##
        self.qualityFrame: Optional[CTkFrame] = None
        self.mp3Button: Optional[CTkCheckBox] = None
        self.mp4Button: Optional[CTkCheckBox] = None
        self.availableMp3Qualities: Optional[List[str]] = None
        self.qualityVarMp3: Optional[StringVar] = None
        self.mp3QualityMenu: Optional[CTkOptionMenu] = None
        self.qualityVarMp4Sound: Optional[StringVar] = None
        self.mp4SoundQualityMenu: Optional[CTkOptionMenu] = None
        self.availableMp4Qualities: Optional[List[str]] = None
        self.qualityVarMp4: Optional[StringVar] = None
        self.mp4QualityMenu: Optional[CTkOptionMenu] = None

        ## Path Frame ##
        self.pathFrame: Optional[CTkFrame] = None
        self.outputEntry: Optional[CTkEntry] = None
        self.outputButton: Optional[CTkButton] = None
        self.downloadButton: Optional[CTkButton] = None

        ## Output Frame ##
        self.outputFrame: Optional[CTkFrame] = None
        self.consoleText: Optional[CTkTextbox] = None
        self.progressBar: Optional[CTkProgressBar] = None
        self.progressLabel: Optional[CTkLabel] = None
        self.outputHandler: Optional[OutputHandler] = None
        self.streamHandler: Optional[StreamHandler] = None

        ## Download Thread ##
        self.downloadThread: Optional[Thread] = None

        ## Advanced Options Variables ##
        self.optionPostProcess: Optional[IntVar] = None
        self.optionThumbnail: Optional[IntVar] = None
        self.optionSubtitles: Optional[IntVar] = None
        self.optionTimeout: Optional[StringVar] = None
        self.optionSound: Optional[IntVar] = None
        self.optionShutdown: Optional[IntVar] = None
        self.optionJSON: Optional[IntVar] = None
        self.optionJSONPath: Optional[StringVar] = None

        ## GUI Setup ##
        self.setupGui()

        ## Hint Message ##
        self.outputHandler.write("Hint: Advanced options can be opened with CTRL + O")

        ## Starting Loops ##
        self.root.after(100, self.updateProgress)
        self.root.mainloop()

    def setupGui(self) -> None:
        """
        Sets up the entire GUI by configuring the main window and calling methods to set up each individual frame.

        :return: None.
        """

        set_appearance_mode("dark")
        set_default_color_theme(fr"{path.dirname(__file__)}\themes\blue.json")

        self.root = CTk()
        self.root.title("8K Video Downloader | Version 8.0")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)

        self.optionInstallPacks = IntVar()
        self.optionMp3 = IntVar()
        self.optionMp4 = IntVar()

        self.scrollableRoot = CTkScrollableFrame(master=self.root, width=380, height=580, fg_color="#1D1E1E",
                                                 bg_color="#1D1E1E")
        self.scrollableRoot.pack(pady=0, padx=0, fill="both", expand=True)

        self.setupURLFrame()
        self.setupQualityFrame()
        self.setupPathFrame()
        self.setupOutputFrame()
        self.setupAdvancedOptions()
        self.setupStreamAndOutput()

        self.root.bind('<Control-o>', self.showAdvancedOptions)

        self.validUrlIcon = CTkImage(Image.open(path.join(path.abspath(path.dirname(__file__)), "media",
                                                          "valid.png")).resize((20, 20)))
        self.invalidUrlIcon = CTkImage(Image.open(path.join(path.abspath(path.dirname(__file__)), "media",
                                                            "invalid.png")).resize((20, 20)))
        self.checkURL()

    def setupURLFrame(self) -> None:
        """
        Sets up the URL frame by configuring the URL input field and download buttons.

        :return: None.
        """

        self.urlFrame = CTkFrame(self.scrollableRoot)
        self.urlFrame.pack(fill="x", padx=15, pady=15)

        self.urlFrame.columnconfigure(0, weight=1)
        self.urlFrame.columnconfigure(1, weight=0)

        self.optionUrl = StringVar()
        self.urlEntry = CTkEntry(self.urlFrame, width=260, textvariable=self.optionUrl)
        self.urlEntry.tooltip = ToolTip(self.urlEntry, self.tooltips.get('urlEntry'), self.root)
        self.urlEntry.insert(0, "Enter/Paste URL here ...")
        self.urlEntry.bind("<FocusIn>", lambda _EVENT: self.urlEntry.delete(0, END) if
                           self.urlEntry.get() == "Enter/Paste URL here ..." else None)
        self.urlEntry.bind("<FocusOut>", lambda _EVENT: self.urlEntry.insert(0, "Enter/Paste URL "
                           "here ...") if self.urlEntry.get() == "" else None)
        self.urlEntry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.urlIconLabel = CTkLabel(self.urlFrame, image=self.invalidUrlIcon, text="")
        self.urlIconLabel.tooltip = ToolTip(self.urlIconLabel, self.tooltips.get('urlIconLabel'), self.root)
        self.urlIconLabel.grid(row=0, column=1, padx=(0, 5))

        self.urlButtonVar = StringVar()

        self.playlistButton = CTkButton(self.urlFrame, text="Download Playlist", state='disabled',
                                        command=self.selectPlaylist)
        self.playlistButton.tooltip = ToolTip(self.playlistButton, self.tooltips.get('playlistButton'), self.root)
        self.videoButton = CTkButton(self.urlFrame, text="Download Video", state='disabled',
                                     command=self.selectVideo)
        self.videoButton.tooltip = ToolTip(self.videoButton, self.tooltips.get('videoButton'), self.root)
        self.selectPlaylist()

        self.optionUrl.trace('w', self.checkURL)

    def selectPlaylist(self) -> None:
        """
        Sets the URL button to 'PLAYLIST' and configures the button states.

        :return: None.
        """

        self.urlButtonVar.set("PLAYLIST")
        self.playlistButton.configure(state='disabled', bg_color="white")
        self.videoButton.configure(state='normal', bg_color="black")

    def selectVideo(self) -> None:
        """
        Sets the URL button to 'VIDEO' and configures the button states.

        :return: None.
        """

        self.urlButtonVar.set("VIDEO")
        self.videoButton.configure(state='disabled', bg_color="white")
        self.playlistButton.configure(state='normal', bg_color="black")

    def checkURL(self, *_ARGS: str) -> None:
        """
        Checks the entered URL and displays the appropriate buttons.

        :param _ARGS: Additional arguments. (unused)
        :return: None.
        """

        def validateURL() -> None:
            """
            Sets the specific icon, depending on whether the URL is valid or not.

            :return: None.
            """

            if self.linkManager.isUrlValid(self.optionUrl.get())[0]:
                self.urlIconLabel.configure(image=self.validUrlIcon)

            else:
                self.urlIconLabel.configure(image=self.invalidUrlIcon)

        self.root.after(0, validateURL)

        if search(r"&list=RD[a-zA-Z0-9_-]+", self.optionUrl.get()):
            self.videoButton.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.selectVideo()

        elif search(r"&list=[a-zA-Z0-9_-]{34}(?=&|$)", self.optionUrl.get()):
            self.playlistButton.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.videoButton.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.selectPlaylist()

        elif search(r"&list=[a-zA-Z0-9_-]{26}(?=&|$)", self.optionUrl.get()):
            self.videoButton.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.selectVideo()

        else:
            self.playlistButton.grid_forget()
            self.videoButton.grid_forget()

    def setupQualityFrame(self) -> None:
        """
        Sets up the Quality frame by configuring the MP3 and MP4 checkboxes and quality menus.

        :return: None.
        """

        self.qualityFrame = CTkFrame(self.scrollableRoot)
        self.qualityFrame.pack(fill="x", padx=15, pady=15)

        self.mp3Button = CTkCheckBox(self.qualityFrame, text="MP3 Download", variable=self.optionMp3,
                                     command=lambda: self.mp3QualityMenu.grid() if self.optionMp3.get() else
                                     self.mp3QualityMenu.grid_remove())
        self.mp3Button.tooltip = ToolTip(self.mp3Button, self.tooltips.get('mp3Button'), self.root)
        self.mp3Button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.mp4Button = CTkCheckBox(self.qualityFrame, text="MP4 Download", variable=self.optionMp4,
                                     command=lambda: (self.mp4QualityMenu.grid() if self.optionMp4.get() else
                                                      self.mp4QualityMenu.grid_remove(), self.mp4SoundQualityMenu.grid()
                                                      if self.optionMp4.get() else
                                                      self.mp4SoundQualityMenu.grid_remove()))
        self.mp4Button.tooltip = ToolTip(self.mp4Button, self.tooltips.get('mp4Button'), self.root)
        self.mp4Button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.availableMp3Qualities = ['Low - 128 kbps', 'Medium - 192 kbps', 'High - 256 kbps',
                                      'Very High - 320 kbps']
        self.qualityVarMp3 = StringVar(value=self.availableMp3Qualities[3])
        self.mp3QualityMenu = CTkOptionMenu(self.qualityFrame, variable=self.qualityVarMp3,
                                            values=self.availableMp3Qualities)
        self.mp3QualityMenu.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.mp3QualityMenu.grid_remove()

        self.qualityVarMp4Sound = StringVar(value=self.availableMp3Qualities[3])
        self.mp4SoundQualityMenu = CTkOptionMenu(self.qualityFrame, variable=self.qualityVarMp4Sound,
                                                 values=self.availableMp3Qualities)
        self.mp4SoundQualityMenu.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.mp4SoundQualityMenu.grid_remove()

        self.availableMp4Qualities = ['SD - 360p', 'HD - 720p', 'FHD - 1080p', 'QHD - 1440p', '4K - 2160p',
                                      '8K - 4320p']
        self.qualityVarMp4 = StringVar(value=self.availableMp4Qualities[2])
        self.mp4QualityMenu = CTkOptionMenu(self.qualityFrame, variable=self.qualityVarMp4,
                                            values=self.availableMp4Qualities)
        self.mp4QualityMenu.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.mp4QualityMenu.grid_remove()

    def setupPathFrame(self) -> None:
        """
        Sets up the Path frame by configuring the output path entry field and buttons.

        :return: None.
        """

        self.pathFrame = CTkFrame(self.scrollableRoot)
        self.pathFrame.pack(fill="x", padx=15, pady=15)

        self.outputEntry = CTkEntry(self.pathFrame, width=300)
        self.outputEntry.tooltip = ToolTip(self.outputEntry, self.tooltips.get('outputEntry'), self.root)
        self.outputEntry.insert(0, "Enter/Browse output path ...")
        self.outputEntry.bind("<FocusIn>", lambda _EVENT: self.outputEntry.delete(0, END) if
                              self.outputEntry.get() == "Enter/Browse output path ..." else None)
        self.outputEntry.bind("<FocusOut>", lambda _EVENT: self.outputEntry.insert(0, "Enter/Browse "
                              "output path ...") if self.outputEntry.get() == "" else None)
        self.outputEntry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.outputButton = CTkButton(self.pathFrame, text="Browse..", command=lambda: self.openPathDialog(
            self.outputEntry))
        self.outputButton.tooltip = ToolTip(self.outputButton, self.tooltips.get('outputButton'), self.root)
        self.outputButton.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.downloadButton = CTkButton(self.scrollableRoot, text="Start Download", command=self.startDownload)
        self.downloadButton.tooltip = ToolTip(self.downloadButton, self.tooltips.get('downloadButton'), self.root)
        self.downloadButton.pack(padx=15, pady=15)

    @staticmethod
    def openPathDialog(ENTRY: CTkEntry, FILE: bool = False, PARENT_WINDOW: Optional[CTkToplevel] = None) -> None:
        """
        Opens a dialog to select the output path.

        :param ENTRY: Entry where file path should be inserted.
        :param FILE: wether file (JSON format) or directory should be opened.
        :param PARENT_WINDOW: Parent window to open the dialog.

        :return: None.
        """

        root2 = CTk()
        root2.withdraw()

        ENTRY.delete(0, END)

        if FILE and PARENT_WINDOW:
            PARENT_WINDOW.attributes('-topmost', 0)
            tmp = askopenfile(filetypes=[("JSON files", "*.json")])
            loc_path = tmp.name if tmp is not None else ""
            PARENT_WINDOW.attributes('-topmost', 1)

        else:
            loc_path = askdirectory()

        root2.destroy()
        ENTRY.delete(0, END)
        ENTRY.insert(0, loc_path)

    def setupOutputFrame(self) -> None:
        """
        Sets up the Output frame by configuring the console text area, progress bar, and progress label.

        :return: None.
        """

        self.outputFrame = CTkFrame(self.scrollableRoot)
        self.outputFrame.pack(fill="x", padx=15, pady=15)

        self.consoleText = CTkTextbox(self.outputFrame, width=335, height=200, activate_scrollbars=False)
        self.consoleText.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.consoleText.configure(state="disabled")

        self.progressBar = CTkProgressBar(master=self.outputFrame, width=200, height=20, corner_radius=10)
        self.progressBar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.progressBar.set(0.0)

        self.progressLabel = CTkLabel(master=self.outputFrame, text="0%", bg_color="transparent",
                                      text_color="white")
        self.progressLabel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.progressLabel.configure(width=-1, height=20)

    def updateProgress(self) -> None:
        """
        Regularly updates the progress bar every 100ms.

        :return: None.
        """

        try:
            self.progressBar.set(self.downloadManager.downloadProgress / 100.0)
            self.progressLabel.configure(text=f"{self.downloadManager.downloadProgress}%")

        except Exception as ERR_02:
            log.error(f"[GUIManager.py@updateProgress] Error updating progress: {ERR_02}", exc_info=True)

        finally:
            self.root.after(100, self.updateProgress)

    def setupStreamAndOutput(self) -> None:
        """
        Sets up the Output- and StreamHandler for the application.

        :return: None.
        """

        self.outputHandler = OutputHandler(root=self.root, outputWidget=self.consoleText)
        self.streamHandler = StreamHandler()
        self.root.after(100, self.outputHandler.updateConsoleFromLog)

    def setupAdvancedOptions(self) -> None:
        self.optionPostProcess = IntVar(value=1)
        self.optionThumbnail = IntVar(value=1)
        self.optionSubtitles = IntVar(value=1)
        self.optionTimeout = StringVar(value=10)
        self.optionSound = IntVar(value=1)
        self.optionShutdown = IntVar(value=0)
        self.optionJSON = IntVar(value=0)
        self.optionJSONPath = StringVar(value="")

    def showAdvancedOptions(self, _EVENT: Optional[Event] = None) -> None:
        """
        Opens a new window with advanced options.

        :param _EVENT: The triggering event. (unused)
        :return: None.
        """

        if "advanced_options" in self.openWindows:
            window = self.openWindows["advanced_options"]
            try:
                window.focus()
                return

            except TclError:
                pass

        advanced_options_window: CTkToplevel = CTkToplevel(self.root)
        self.openWindows["advanced_options"] = advanced_options_window

        def onClose() -> None:
            """
            Function that is called when closing.
            Deletes the window from the active windows and destroys it.

            :return: None.
            """

            del self.openWindows["advanced_options"]
            advanced_options_window.destroy()

        advanced_options_window.title("Advanced Options")
        advanced_options_window.geometry("400x450")
        advanced_options_window.resizable(False, False)
        advanced_options_window.attributes('-topmost', 1)

        def validateTimeout(*_ARGS: str) -> None:
            """
            Checks whether the timeout value entered is in the range from 0 to 999 and clamps it if necessary.

            :param _ARGS: Additional arguments. (unused)
            :return: None.
            """

            if not self.optionTimeout.get().isdigit():
                self.optionTimeout.set("0")

            elif int(self.optionTimeout.get()) > 999:
                self.optionTimeout.set("999")

        self.optionTimeout.trace_add('write', validateTimeout)

        frame: CTkFrame = CTkFrame(advanced_options_window)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        postprocess_check: CTkCheckBox = CTkCheckBox(frame, text="Use Postprocessor", variable=self.optionPostProcess)
        postprocess_check.grid(row=0, column=0, columnspan=2, sticky='w', pady=(10, 5), padx=(10, 0))
        postprocess_check.tooltip = ToolTip(postprocess_check, self.tooltips.get('postprocess_check'),
                                            advanced_options_window)

        thumbnail_check: CTkCheckBox = CTkCheckBox(frame, text="Add Thumbnail", variable=self.optionThumbnail)
        thumbnail_check.grid(row=1, column=0, columnspan=2, sticky='w', pady=5, padx=(10, 0))
        thumbnail_check.tooltip = ToolTip(thumbnail_check, self.tooltips.get('thumbnail_check'),
                                          advanced_options_window)

        subtitles_check: CTkCheckBox = CTkCheckBox(frame, text="Add Subtitles", variable=self.optionSubtitles)
        subtitles_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5, padx=(10, 0))
        subtitles_check.tooltip = ToolTip(subtitles_check, self.tooltips.get('subtitles_check'),
                                          advanced_options_window)

        timeout_entry: CTkEntry = CTkEntry(frame, textvariable=self.optionTimeout, width=50)
        timeout_entry.grid(row=3, column=0, sticky='w', pady=5, padx=(10, 5))
        timeout_entry.tooltip = ToolTip(timeout_entry, self.tooltips.get('timeout_entry'), advanced_options_window)

        timeout_label: CTkLabel = CTkLabel(frame, text="Timeout")
        timeout_label.grid(row=3, column=0, sticky='w', pady=5, padx=70)

        sound_check: CTkCheckBox = CTkCheckBox(frame, text="Sound after Download", variable=self.optionSound)
        sound_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=5, padx=(10, 0))
        sound_check.tooltip = ToolTip(sound_check, self.tooltips.get('sound_check'),
                                      advanced_options_window)

        shutdown_check: CTkCheckBox = CTkCheckBox(frame, text="Shutdown after Download", variable=self.optionShutdown)
        shutdown_check.grid(row=5, column=0, columnspan=2, sticky='w', pady=5, padx=(10, 0))
        shutdown_check.tooltip = ToolTip(shutdown_check, self.tooltips.get('shutdown_check'),
                                         advanced_options_window)

        def toggleJSONFields() -> None:
            """
            Activates or deactivates the JSON fields when the corresponding button is pressed.

            :return: None.
            """

            if self.optionJSON.get():
                json_entry.configure(state="normal")
                json_browse_button.configure(state="normal")
                self.urlEntry.configure(state="disabled")
                self.urlEntry.delete(0, END)

            else:
                json_entry.configure(state="disabled")
                json_entry.delete(0, END)
                json_browse_button.configure(state="disabled")
                self.urlEntry.configure(state="normal")

        json_output_check: CTkCheckBox = CTkCheckBox(frame, text="Use JSON File", variable=self.optionJSON,
                                                     command=toggleJSONFields)
        json_output_check.grid(row=6, column=0, columnspan=2, sticky='w', pady=5, padx=(10, 0))
        json_output_check.tooltip = ToolTip(json_output_check, self.tooltips.get('json_output_check'),
                                            advanced_options_window)

        json_entry: CTkEntry = CTkEntry(frame, textvariable=self.optionJSONPath, width=200)
        json_entry.grid(row=7, column=0, sticky='w', pady=5, padx=(10, 5))
        json_entry.tooltip = ToolTip(json_entry, self.tooltips.get('json_entry'), advanced_options_window)

        json_browse_button: CTkButton = CTkButton(frame, text="Browse..", command=lambda:
                                                  self.openPathDialog(json_entry, FILE=True,
                                                                      PARENT_WINDOW=advanced_options_window))
        json_browse_button.grid(row=8, column=0, sticky='w', pady=5, padx=(10, 0))
        json_browse_button.tooltip = ToolTip(json_browse_button, self.tooltips.get('json_browse_button'),
                                             advanced_options_window)

        okay_button: CTkButton = CTkButton(frame, text="Okay", command=lambda: advanced_options_window.destroy())
        okay_button.grid(row=9, column=0, sticky='e', padx=200, pady=30)
        okay_button.tooltip = ToolTip(okay_button, self.tooltips.get('okay_button'), advanced_options_window)

        toggleJSONFields()
        advanced_options_window.protocol("WM_DELETE_WINDOW", onClose)

    def getOptionDict(self, FLAG: str) -> Dict[str, Any]:
        """
        Creates the option dictionary for the DownloadManager.

        :param FLAG: Flag to specify MP3 or MP4 download.
        :return: dict: Dictionary of options.
        """

        if not self.optionJSON.get() and not self.linkManager.isUrlValid(self.urlEntry.get())[0]:
            raise ValueError("Invalid URL!")

        if not path.exists(self.outputEntry.get()):
            raise ValueError("Invalid Path!")

        if not self.optionMp3.get() and not self.optionMp4.get():
            raise ValueError("Invalid Format!")

        def extractQuality(OPTION: str, UNIT: str) -> int:
            """

            :param OPTION: Option to extract quality.
            :param UNIT: Unit to extract quality. (kbps, p)

            :return: Quality as an integer
            """

            matched = search(rf'(\d+)\s*{UNIT}', OPTION)
            return int(matched.group(1)) if matched else 0

        options: Dict[str, Any] = \
        {
            'URL': self.urlEntry.get() if not self.optionJSON.get() else None,
            'PATH': path.join(self.outputEntry.get(), FLAG.upper()) if self.optionMp3.get() and self.optionMp4.get()
            else self.outputEntry.get(),
            'FLAG': self.urlButtonVar.get().lower(),
            'FORMAT': FLAG.lower(),
            'QUAL': ((extractQuality(self.qualityVarMp3.get(), 'kbps')),
                     (extractQuality(self.qualityVarMp4Sound.get(), 'kbps'),
                      extractQuality(self.qualityVarMp4.get(), 'p'))),
            'POSTPROCESS': bool(self.optionPostProcess.get()),
            'THUMBNAIL': bool(self.optionThumbnail.get()),
            'SUBTITLES': bool(self.optionSubtitles.get()),
            'TIMEOUT': int(self.optionTimeout.get()) if self.optionTimeout.get().isdigit() else 10,
            'SILENT_OUTPUT': False,
            'USE_JSON': bool(self.optionJSON.get()),
            'JSON_PATH': self.optionJSONPath.get() if self.optionJSON.get() else None
        }

        log.debug(f"[GUIManager.py@getOptionDict] Options: {options}")
        return options

    def startDownload(self) -> None:
        """
        Starts the download process in a separate thread.

        :return: None.
        """

        if self.downloadThread and self.downloadThread.is_alive():
            self.messageBoxManager.showInfo("A download is already in progress.")
            log.error("[GUIManager.py@startDownload] A download is already in progress.")
            return

        def runDownload() -> None:
            """
            Runs the download process in a separate thread using the event loop.

            :return: None.
            """

            loop: AbstractEventLoop = new_event_loop()
            set_event_loop(loop)
            loop.run_until_complete(self.downloadTask())
            loop.close()

        def checkShutdown() -> None:
            """
            Checks if download is finished and closes application with code 1000 if necessary.

            :return: None.
            """

            if self.downloadThread and self.downloadThread.is_alive():
                self.root.after(1000, checkShutdown)

            elif self.optionShutdown.get():
                self.root.after(5000, lambda: self.onClose(1000))

        self.downloadThread = Thread(target=runDownload)
        self.downloadThread.start()

        self.root.after(1000, checkShutdown)

    async def downloadTask(self) -> bool:
        """
        Handles the download process in a separate thread.

        :return: bool: True or False, depending on whether an error has occurred.
        """

        startTime: float = time()

        try:
            isSuccess: bool = False

            if self.optionMp3.get():
                log.info("[GUIManager.py@downloadThreadFunc] MP3 download started ...")
                self.outputHandler.write("MP3 download started ...")

                await self.downloadManager.setOptions(self.getOptionDict(FLAG="MP3"))
                isSuccess = True if await self.downloadManager.downloadVideo() else False

            if self.optionMp4.get():
                log.info("[GUIManager.py@downloadThreadFunc] MP4 download started ...")
                self.outputHandler.write("MP4 download started ...")

                await self.downloadManager.setOptions(self.getOptionDict(FLAG="MP4"))
                isSuccess = True if await self.downloadManager.downloadVideo() else False

            if not self.optionMp3.get() and not self.optionMp4.get():
                if self.optionShutdown.get():
                    self.messageBoxManager.showError("No format specified!")

                log.error("[GUIManager.py@downloadThreadFunc] No format specified!")
                isSuccess = False

        except Exception as ERR_03:
            if not self.optionShutdown.get():
                self.messageBoxManager.showError(f"{ERR_03}")

            log.error(f"[GUIManager.py@downloadThreadFunc] Exception (ERR_03): {ERR_03}", exc_info=True)
            isSuccess = False

        finally:
            if isSuccess:
                if not self.optionShutdown.get():
                    self.messageBoxManager.showCheckmark("The download is complete ...")

                self.outputHandler.write("The download is complete ...")
                log.info("The download is complete ...")

            else:
                if not self.optionShutdown.get():
                    self.messageBoxManager.showError("Download of the file[s] aborted ...")

                self.outputHandler.write("Download of the file[s] aborted ...")
                log.error("Download of the file[s] aborted ...")

            self.outputHandler.write(f"Download Task finished in {time() - startTime:.2f} seconds")

            self.outputHandler.write("Deleting console in 5 seconds ...")
            self.root.after(5000, self.outputHandler.clearFile)

            if self.optionSound.get():
                MediaPlayer(path.join(path.dirname(path.abspath(__file__)), 'media', 'notifysound.mp3')).play()

            return isSuccess

    def onClose(self, EXIT_CODE: int = 0) -> None:
        """
        Handles the event of closing the main window.
        Exits the application.

        :param EXIT_CODE: Exit code of the application.
        :return: None.
        """

        if self.downloadThread and self.downloadThread.is_alive():
            log.info("[GUIManager.py@onClose] Thread is running, aborted ...")
            self.messageBoxManager.showInfo("Finish the download before closing!")
            return

        log.info("[GUIManager.py@onClose] Application closed by user.")
        self.root.destroy()

        loop = get_event_loop()
        if loop.is_running():
            log.info("[GUIManager.py@onClose] Closing event loop...")
            loop.stop()
            loop.close()

        raise SystemExit(EXIT_CODE)
