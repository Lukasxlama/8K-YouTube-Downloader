##################################
# Projekt: 8K YouTube Downloader #
# Dateiname: __main__.py         #
# Version: 6.0                   #
# Autor: lukasxlama              #
##################################


### Imports ###
try:
    from tkinter.filedialog import askdirectory
    from get_video_informations import *
    from download_video import *
    from messageboxes import *
    from os import path
    import customtkinter as ctk
    import threading as t
    import tkinter as tk
    import sys
except ImportError:
    exit()


### Tkinter GUI ###
## Startwerte ##
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(fr"{path.dirname(__file__)}\themes\blue.json")

root = ctk.CTk()
root.title("8k YouTube Downloader | Version 6.0")
root.geometry("400x600")
root.resizable(False, False)

install_packs = ctk.IntVar()
mp3 = ctk.IntVar()
mp4 = ctk.IntVar()


## Entry Widget - URL  & Button Widgets - URL ##
def on_url_entry_click(event):  # NOQA
    if url_entry.get() == "Gib eine URL ein...":
        url_entry.delete(0, "end")

def on_url_focus_out(event):  # NOQA
    if url_entry.get() == "":
        url_entry.insert(0, "Gib eine URL ein...")

def select_playlist():
    global url_button_var  # NOQA
    url_button_var = "PLAYLIST"

    playlist_button.configure(state='disabled', bg_color="white")
    video_button.configure(state='normal', bg_color="black")

    print("Playlist für den Download festgelegt..\n")

def select_video():
    global url_button_var  # NOQA
    url_button_var = "VIDEO"

    video_button.configure(state='disabled', bg_color="white")
    playlist_button.configure(state='normal', bg_color="black")

    print("Video für den Download festgelegt..\n")

def check_url(*args):  # NOQA
    if "&list=" in url_var.get():
        playlist_button.grid(row=1, column=0, padx=10, pady=10)
        video_button.grid(row=2, column=0, padx=10, pady=10)
    else:
        playlist_button.grid_forget()
        video_button.grid_forget()


url_frame = ctk.CTkFrame(root)
url_frame.pack(padx=15, pady=15)

url_var = ctk.StringVar()
url_entry = ctk.CTkEntry(url_frame, width=300, textvariable=url_var)
url_entry.insert(0, "Gib eine URL ein...")
url_entry.bind("<FocusIn>", on_url_entry_click)
url_entry.bind("<FocusOut>", on_url_focus_out)
url_entry.grid(row=0, column=0, padx=10, pady=10)

url_button_var = ctk.StringVar()

playlist_button = ctk.CTkButton(url_frame, text="Download Playlist", state='disabled', command=select_playlist)
video_button = ctk.CTkButton(url_frame, text="Download Video", state='disabled', command=select_video)
select_playlist()

url_var.trace('w', check_url)


## Checkbox Widget - MP3 ##
mp3_button = ctk.CTkCheckBox(root, text="MP3 Download", variable=mp3)
mp3_button.pack(padx=5, pady=5)


## Checkbox Widget - MP4 ##
mp4_button = ctk.CTkCheckBox(root, text="MP4 Download", variable=mp4)
mp4_button.pack(padx=5, pady=5)


## Entry Widget - Ausgabepfad ##
def on_output_entry_click(event):  # NOQA
    if output_entry.get() == "Gib einen Ausgabepfad ein...":
        output_entry.delete(0, "end")

def on_output_focus_out(event):  # NOQA
    if output_entry.get() == "":
        output_entry.insert(0, "Gib einen Ausgabepfad ein...")


output_entry = ctk.CTkEntry(root, width=300)
output_entry.insert(0, "Gib einen Ausgabepfad ein...")
output_entry.bind("<FocusIn>", on_output_entry_click)
output_entry.bind("<FocusOut>", on_output_focus_out)
output_entry.pack(padx=10, pady=10)


## Button Widget - Ausgabepfad Explorer ##
def get_path():
    root2 = ctk.CTk()
    root2.withdraw()
    output_entry.delete(0, "end")
    loc_path = askdirectory()
    root2.destroy()
    output_entry.insert(0, loc_path)


output_button = ctk.CTkButton(root, text="Durchsuchen..", command=get_path)
output_button.pack()


## Button - Download starten ##
download_thread=None

def start_download():
    global download_thread

    if download_thread and download_thread.is_alive():
        show_info("Ein Download ist bereits aktiv..")
        return -1

    def download_thread_func():
        return_val_url = get_url_informations(url_entry.get(), url_button_var)

        if return_val_url != "URL_ERROR":
            URL = url_entry.get()

        else:
            show_error("Ungültige URL angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return -1

        if path.exists(output_entry.get()):
            PATH = output_entry.get()

        else:
            show_error("Ungültiger Pfad angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return -1

        if bool(mp3.get()) and bool(mp4.get()):
            print("\nMP3 & MP4 Download gestartet..")
            return_val_mp3 = download_mp3(URL, fr"{PATH}\MP3", url_button_var)
            return_val_mp4 = download_mp4(URL, fr"{PATH}\MP4", url_button_var)

            if return_val_mp3 == 1 and return_val_mp4 == 1:
                show_checkmark("Der Download wurde abgeschlossen..")
                return 1

            elif return_val_mp3 == -1 or return_val_mp4 == -1:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                return -1

        elif bool(mp3.get()):
            print("\nMP3 Download gestartet..")
            return_val_mp3 = download_mp3(URL, fr"{PATH}", url_button_var)

            if return_val_mp3 == 1:
                show_checkmark("Der Download wurde abgeschlossen..")
                return 1

            elif return_val_mp3 == -1:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                return -1

        elif bool(mp4.get()):
            print("\nMP4 Download gestartet..")
            return_val_mp4 = download_mp4(URL, fr"{PATH}", url_button_var)

            if return_val_mp4 == 1:
                show_checkmark("Der Download wurde abgeschlossen..")
                return 1

            elif return_val_mp4 == -1:
                show_error("Es ist ein unerwarteter Fehler aufgetreten!")
                return -1

        else:
            show_error("Kein Format Angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return -1

    download_thread = t.Thread(target=download_thread_func)
    download_thread.start()

download_button = ctk.CTkButton(root, text="Download starten", command=start_download)
download_button.pack(padx=15, pady=15)


## Text Widget - Konsolenausgabe ##
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

console_text = ctk.CTkTextbox(root, width=800, height=800)
console_text.pack()

console_redirector = ConsoleRedirector(console_text)


## Hauptereignisschleife starten ##
root.mainloop()
