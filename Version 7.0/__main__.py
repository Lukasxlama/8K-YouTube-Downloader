##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: __main__.py         #
# Version: 7.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    ## Logging ##
    from LoggerConfig import getLoggerConfig
    import logging as log

    ## GUI ##
    from tkinter.filedialog import askdirectory
    from tkinter import ttk
    import customtkinter as ctk
    import tkinter as tk

    ## Eigene Module ##
    from ExtractVideoID import *
    from DownloadVideo import *
    from MessageBoxes import *

    ## Betriebssystemzugriff ##
    from os import path
    import sys

    ## Threads & RegEx ##
    import threading as t
    from re import sub

except ImportError:
    print(f"[__main__.py] Fehler beim Import: {e}")
    sys.exit(-810)


### Logger starten ###
getLoggerConfig()


### Tkinter GUI ###
## Startwerte ##
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(fr"{path.dirname(__file__)}\themes\blue.json")

root = ctk.CTk()
root.title("8k YouTube Downloader | Version 7.0")
root.geometry("400x600")
root.resizable(False, False)

install_packs = ctk.IntVar()
mp3 = ctk.IntVar()
mp4 = ctk.IntVar()


## Scrollable Frame ##
rRoot = ctk.CTkScrollableFrame(master=root, width=380, height=580, fg_color="#1D1E1E", bg_color="#1D1E1E")
rRoot.pack(pady=0, padx=0, fill="both", expand=True)


## Entry Widget - URL  & Button Widgets - URL ##
def on_url_entry_click(event):
    if url_entry.get() == "Gib eine URL ein...":
        url_entry.delete(0, "end")

def on_url_focus_out(event):
    if url_entry.get() == "":
        url_entry.insert(0, "Gib eine URL ein...")

def select_playlist():
    global url_button_var
    url_button_var = "PLAYLIST"

    playlist_button.configure(state='disabled', bg_color="white")
    video_button.configure(state='normal', bg_color="black")

def select_video():
    global url_button_var
    url_button_var = "VIDEO"

    video_button.configure(state='disabled', bg_color="white")
    playlist_button.configure(state='normal', bg_color="black")

def check_url(*args):
    if "&list=" in url_var.get():
        playlist_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        video_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    else:
        playlist_button.grid_forget()
        video_button.grid_forget()


## URL Frame ##
url_frame = ctk.CTkFrame(rRoot)
url_frame.pack(fill="x", padx=15, pady=15)

url_var = ctk.StringVar()
url_entry = ctk.CTkEntry(url_frame, width=300, textvariable=url_var)
url_entry.insert(0, "Gib eine URL ein...")
url_entry.bind("<FocusIn>", on_url_entry_click)
url_entry.bind("<FocusOut>", on_url_focus_out)
url_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

url_button_var = ctk.StringVar()

playlist_button = ctk.CTkButton(url_frame, text="Download Playlist", state='disabled', command=select_playlist)
video_button = ctk.CTkButton(url_frame, text="Download Video", state='disabled', command=select_video)
select_playlist()

url_var.trace('w', check_url)


## Format Frame ##
quality_frame = ctk.CTkFrame(rRoot)
quality_frame.pack(fill="x", padx=15, pady=15)

# Checkbox Widget - MP3 #
def toggle_mp3_quality_menu():
    if mp3.get() == 1:
        mp3_quality_menu.grid()
    else:
        mp3_quality_menu.grid_remove()

mp3_button = ctk.CTkCheckBox(quality_frame, text="MP3 Download", variable=mp3, command=toggle_mp3_quality_menu)
mp3_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Checkbox Widget - MP4 #
def toggle_mp4_quality_menu():
    if mp4.get() == 1:
        mp4_quality_menu.grid()
        mp4_sound_quality_menu.grid()
    else:
        mp4_quality_menu.grid_remove()
        mp4_sound_quality_menu.grid_remove()

mp4_button = ctk.CTkCheckBox(quality_frame, text="MP4 Download", variable=mp4, command=toggle_mp4_quality_menu)
mp4_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Option-Menu Widget - MP3 #
available_mp3_qualities = ['Niedrig - 128 kbps', 'Mittel - 192 kbps', 'Hoch - 256 kbps', 'Sehr hoch - 320 kbps']
quality_var_mp3 = tk.StringVar(value=available_mp3_qualities[3])
mp3_quality_menu = ctk.CTkOptionMenu(quality_frame, variable=quality_var_mp3, values=available_mp3_qualities)
mp3_quality_menu.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
mp3_quality_menu.grid_remove()

# Option-Menu Widget - MP4 #
quality_var_mp4_sound = tk.StringVar(value=available_mp3_qualities[3])
mp4_sound_quality_menu = ctk.CTkOptionMenu(quality_frame, variable=quality_var_mp4_sound, values=available_mp3_qualities)
mp4_sound_quality_menu.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
mp4_sound_quality_menu.grid_remove()

available_mp4_qualities = ['SD - 360p', 'HD - 720p', 'FHD - 1080p', 'QHD - 1440p', '4K - 2160p', '8K - 4320p']
quality_var_mp4 = tk.StringVar(value=available_mp4_qualities[2])
mp4_quality_menu = ctk.CTkOptionMenu(quality_frame, variable=quality_var_mp4, values=available_mp4_qualities)
mp4_quality_menu.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
mp4_quality_menu.grid_remove()


## Path Frame ##
path_frame = ctk.CTkFrame(rRoot)
path_frame.pack(fill="x", padx=15, pady=15)

# Entry Widget - Ausgabepfad #
def on_output_entry_click(event):
    if output_entry.get() == "Gib einen Ausgabepfad ein...":
        output_entry.delete(0, "end")

def on_output_focus_out(event):
    if output_entry.get() == "":
        output_entry.insert(0, "Gib einen Ausgabepfad ein...")


output_entry = ctk.CTkEntry(path_frame, width=300)
output_entry.insert(0, "Gib einen Ausgabepfad ein...")
output_entry.bind("<FocusIn>", on_output_entry_click)
output_entry.bind("<FocusOut>", on_output_focus_out)
output_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)


# Button Widget - Ausgabepfad Explorer #
def get_path():
    root2 = ctk.CTk()
    root2.withdraw()
    output_entry.delete(0, "end")
    loc_path = askdirectory()
    root2.destroy()
    output_entry.insert(0, loc_path)

output_button = ctk.CTkButton(path_frame, text="Durchsuchen..", command=get_path)
output_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Button - Download starten #
download_thread=None

def start_download():
    global download_thread

    if download_thread and download_thread.is_alive():
        show_info("Ein Download ist bereits aktiv..")
        log.error("[__main__.py] Ein Download ist bereits aktiv..")
        return False

    def download_thread_func():
        return_val_url = getVideoID(url_entry.get(), url_button_var)
        selected_mp3_quality = sub("\D", "", quality_var_mp3.get())
        selected_mp4_sound_quality = sub("\D", "", quality_var_mp4_sound.get())
        selected_mp4_quality = sub("\D", "", quality_var_mp4.get())
        quality_tuple = (selected_mp3_quality, (selected_mp4_sound_quality, selected_mp4_quality))

        if return_val_url:
            URL = url_entry.get()

        else:
            show_error("Ungültige URL angegeben!")
            log.error("[__main__.py] Ungültige URL angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return False

        if path.exists(output_entry.get()):
            PATH = output_entry.get()

        else:
            show_error("Ungültiger Pfad angegeben!")
            log.error("[__main__.py] Ungültiger Pfad angegeben")
            print("\nDownload der Datei[en] abgebrochen..")
            return False

        if bool(mp3.get()) and bool(mp4.get()):
            print("\nMP3 & MP4 Download gestartet..")
            log.info("\n[__main__.py] MP3 & MP4 Download gestartet..")
            return_val_mp3 = downloadVideo(URL, fr"{PATH}\MP3", url_button_var, "MP3", quality_tuple)
            return_val_mp4 = downloadVideo(URL, fr"{PATH}\MP4", url_button_var, "MP4", quality_tuple)

            if return_val_mp3 and return_val_mp4:
                show_checkmark("Der Download wurde abgeschlossen..")
                log.info("[__main__.py] Der Download wurde abgeschlossen..")
                return True

            elif not return_val_mp3 or not return_val_mp4:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                log.error("[__main__.py] Es ist ein unerwarteter Fehler aufgetreten!")
                return False

        elif bool(mp3.get()):
            print("\nMP3 Download gestartet..")
            log.info("\n[__main__.py] MP3 Download gestartet..")
            return_val_mp3 = downloadVideo(URL, fr"{PATH}\MP3", url_button_var, "MP3", quality_tuple)

            if return_val_mp3:
                show_checkmark("Der Download wurde abgeschlossen..")
                log.info("[__main__.py] Der Download wurde abgeschlossen..")
                return True

            elif not return_val_mp3:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                log.error("[__main__.py] Es ist ein unerwarteter Fehler aufgetreten!")
                return False

        elif bool(mp4.get()):
            print("\nMP4 Download gestartet..")
            log.info("\n[__main__.py] MP4 Download gestartet..")
            return_val_mp4 = downloadVideo(URL, fr"{PATH}\MP4", url_button_var, "MP4", quality_tuple)

            if return_val_mp4:
                show_checkmark("Der Download wurde abgeschlossen..")
                log.info("[__main__.py] Der Download wurde abgeschlossen..")
                return True

            elif not return_val_mp4:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                log.error("[__main__.py] Es ist ein unerwarteter Fehler aufgetreten!")
                return False

        else:
            show_error("Kein Format Angegeben!")
            log.error("[__main__.py] Kein Format angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return False

    download_thread = t.Thread(target=download_thread_func)
    download_thread.start()

download_button = ctk.CTkButton(rRoot, text="Download starten", command=start_download)
download_button.pack(padx=15, pady=15)


## Output Frame ##
output_frame = ctk.CTkFrame(rRoot)
output_frame.pack(fill="x", padx=15, pady=15)

# Text Widget - Konsolenausgabe #
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

    def __del__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

console_text = ctk.CTkTextbox(output_frame, width=335, height=200)
console_text.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

console_redirector = ConsoleRedirector(console_text)

# Progress Bar #
def updateProgress() -> None:
    """
    Prüft regelmäßig den Fortschritt und aktualisiert den Fortschrittsbalken.

    :return: None
    """
    try:
        from DownloadVideo import downloadProgress
        progress_bar.set(downloadProgress / 100.0)
        progress_label.configure(text=f"{downloadProgress}%")
    except Exception as e:
        log.error(f"[__main__.py] Fehler beim Aktualisieren des Fortschritts: {e}", exc_info=e)
    finally:
        root.after(500, updateProgress)

progress_bar = ctk.CTkProgressBar(master=output_frame, width=200, height=20, corner_radius=10)
progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
progress_bar.set(0.0)

progress_label = ctk.CTkLabel(master=output_frame, text="0%", bg_color="transparent", text_color="white")
progress_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
progress_label.configure(width=-1, height=20)

root.after(500, updateProgress)

## Hauptereignisschleife starten ##
root.mainloop()