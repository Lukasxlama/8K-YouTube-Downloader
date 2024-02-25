"""
filename: 8k_downloader_exe.py
author: lukasxlama
version: 2.0 | exe
"""

import customtkinter as ctk
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox, ttk, filedialog
from os import environ, pathsep, path, listdir, rename
from subprocess import Popen
from winreg import OpenKey, QueryValueEx, KEY_ALL_ACCESS, HKEY_CURRENT_USER, SetValueEx, REG_EXPAND_SZ, CloseKey
from PIL import ImageTk, Image
import threading as t
from ttkthemes import ThemedStyle
import sys


def add_ffmpeg_to_path(PATH: str) -> None:
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    value, _ = QueryValueEx(key, 'Path')
    paths = value.split(pathsep)

    if PATH not in paths:
        paths.append(PATH)
        new_value = pathsep.join(paths)
        SetValueEx(key, 'Path', 0, REG_EXPAND_SZ, new_value)
        CloseKey(key)
        environ['PATH'] = new_value

    print("FFMPEG wurde zur Umgebungsvariable 'Path' hinzugefügt..")


def download_yt_dlp():
    Popen(["pip", "install", "yt-dlp"])


def get_IDs(URL: str, PLAYLIST: bool = False) -> str:
    if PLAYLIST:
        return URL.split("?list=")[1]
    elif "youtu.be" in URL:
        return URL.split("/")[3]
    elif "youtube.com/watch?v=" in URL:
        return URL.split("=")[1][:11]
    else:
        messagebox.showerror("Fehler", f"Die URL ist ungültig! (URL = {URL})")
        print("\nDownload der Datei[en] abgebrochen..")


def get_flag(URL: str) -> str:
    if "?list=" in URL:
        return 'playlist'
    elif "?v=" in URL or "youtu.be" in URL:
        return 'file'
    else:
        messagebox.showerror("Fehler", f"Aus der URL konnten keine Informationen gelesen werden! (URL = {URL})")
        print("\nDownload der Datei[en] abgebrochen..")


def download_mp4(URL: str, PATH: str) -> None:
    try:
        FLAG = get_flag(URL)

        if FLAG == 'file':
            print(f"Die URL wurde extrahiert..")

            Popen(['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '-o',
                   f"{PATH}/%(title)s.%(ext)s", '--merge-output-format', 'mp4', get_IDs(URL)],
                  creationflags=subprocess.CREATE_NO_WINDOW)

            print(f"\nDownload der Datei abgeschlossen.. [MP4]")

        elif FLAG == "playlist":
            print(f"Die URL wurde extrahiert..")

            Popen(['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', '-o',
                   f"{PATH}/%(playlist_index)s_%(title)s.%(ext)s", '--merge-output-format', 'mp4',
                   '--yes-playlist', get_IDs(URL, True)],
                  creationflags=subprocess.CREATE_NO_WINDOW)

            print(f"\nDownload der Playlist abgeschlossen.. [MP4]")

        else:
            return

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_01:
        print(f"Fehlermeldung: {Error_01}!")
        messagebox.showerror("Fehler", f"Fehler beim Download: {Error_01}")
        print("\nDownload der Datei[en] abgebrochen..")


def download_mp3(URL: str, PATH: str) -> None:
    try:
        FLAG = get_flag(URL)

        if FLAG == 'file':
            print(f"Die URL wurde extrahiert..")

            Popen(['yt-dlp', '-x', '--audio-format', 'mp3', '-o',
                   f"{PATH}/%(title)s.%(ext)s", get_IDs(URL)],
                  creationflags=subprocess.CREATE_NO_WINDOW)

            print(f"\nDownload der Datei abgeschlossen.. [MP3]")

        elif FLAG == "playlist":
            print(f"Die URL wurde extrahiert..")

            Popen(['yt-dlp', '-x', '--audio-format', 'mp3', '-o',
                   f"{PATH}/%(playlist_index)s_%(title)s.%(ext)s", '--yes-playlist', get_IDs(URL, True)],
                  creationflags=subprocess.CREATE_NO_WINDOW)

            print(f"\nDownload der Playlist abgeschlossen.. [MP3]")
        else:
            return

        for file in listdir(PATH):
            if "_" in file:
                rename(path.join(PATH, file), path.join(PATH, file.split("_", 1)[1]))

    except Exception as Error_02:
        print(f"Fehlermeldung: {Error_02}!")
        messagebox.showerror("Fehler", f"Fehler beim Download: {Error_02}")
        print("\nDownload der Datei[en] abgebrochen..")


### Tkinter GUI ###
## Startwerte ##
root = ctk.CTk()
root.title("8k YouTube Downloader")
root.geometry("400x500")
root.resizable(False, False)

install_packs = ctk.IntVar()
mp3 = ctk.IntVar()
mp4 = ctk.IntVar()

## Checkbox Widget - Abhängigkeiten ##
pack_button = ctk.CTkCheckBox(root, text="Abhängigkeiten installieren", variable=install_packs)
pack_button.pack(padx=10, pady=10)


## Entry Widget - URL ##
def on_url_entry_click(placeholder):
    if url_entry.get() == "Gib eine URL ein...":
        url_entry.delete(0, "end")


def on_url_focus_out(placeholder):
    if url_entry.get() == "":
        url_entry.insert(0, "Gib eine URL ein...")


url_entry = ctk.CTkEntry(root, width=300)
url_entry.insert(0, "Gib eine URL ein...")
url_entry.bind("<FocusIn>", on_url_entry_click)
url_entry.bind("<FocusOut>", on_url_focus_out)
url_entry.pack(padx=15, pady=15)

## Checkbox Widget - MP3 ##
mp3_button = ctk.CTkCheckBox(root, text="MP3 Download", variable=mp3)
mp3_button.pack(padx=5, pady=5)

## Checkbox Widget - MP4 ##
mp4_button = ctk.CTkCheckBox(root, text="MP4 Download", variable=mp4)
mp4_button.pack(padx=5, pady=5)


## Entry Widget - Ausgabepfad ##
def on_output_entry_click(placeholder):
    if output_entry.get() == "Gib einen Ausgabepfad ein...":
        output_entry.delete(0, "end")


def on_output_focus_out(placeholder):
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
    loc_path = filedialog.askdirectory()
    root2.destroy()
    output_entry.insert(0, loc_path)


output_button = ctk.CTkButton(root, text="Durchsuchen..", command=get_path)
output_button.pack()


## Button - Download starten ##
def start_download():
    def download_thread():
        if bool(install_packs.get()):
            download_yt_dlp()
            print("YT-DLP wurde heruntergeladen..")

            add_ffmpeg_to_path(fr"{path.dirname(path.abspath(__file__))}\ffmpeg\bin")

        if url_entry != "" and output_entry != "":
            URL = url_entry.get()
            PATH = output_entry.get()

        else:
            messagebox.showerror("Fehler", "Keine URL oder PATH angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return

        if bool(mp3.get()) and bool(mp4.get()):
            print("MP3 & MP4 Download gestartet..")
            download_mp3(URL, fr"{PATH}\MP3")
            download_mp4(URL, fr"{PATH}\MP4")

        elif bool(mp3.get()):
            print("MP3 Download gestartet..")
            download_mp3(URL, fr"{PATH}")

        elif bool(mp4.get()):
            print("MP4 Download gestartet..")
            download_mp4(URL, fr"{PATH}")

        else:
            messagebox.showerror("Fehler", "Kein Format Angegeben!")
            print("\nDownload der Datei[en] abgebrochen..")
            return

    t.Thread(target=download_thread).start()


download_button = ctk.CTkButton(root, text="Download starten", command=start_download)
download_button.pack(padx=15, pady=15)

## Text Widget - Konsolenausgabe ##
console_text = ctk.CTkTextbox(root, height=200, width=300)
console_text.pack(padx=15, pady=15)


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

    def __del__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr


console_redirector = ConsoleRedirector(console_text)

## Hauptereignisschleife starten ##
root.mainloop()
