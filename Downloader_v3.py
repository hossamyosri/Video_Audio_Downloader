# Import required libraries
import os, re, threading, sys
import customtkinter as tk
from typing import TypedDict
from yt_dlp import YoutubeDL
from tkinter import filedialog, messagebox

# Function to get the correct path for bundled files when using PyInstaller
def resource_path(relative_path):
    try:
        # When running as a bundled executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running the script directly
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set default theme using 'theme.json' <<replace it by your path.>>
tk.set_default_color_theme(resource_path('C:/Users/Hossam/Downloads/V3/theme.json'))

# Define a structure for application settings
class ConfigureOption(TypedDict):
    name: str  # App name
    size: str  # Window size

# Main class to initialize the application
class InitializeApplication:

    # Initialize the application with the main window and UI
    def __init__(self, app: tk.CTk):
        self.app = app  # Assign app instance
        self.isDownloading = False  # Download status flag
        self.createApplicationUI()  # Create UI components

    # Create the UI components of the app
    def createApplicationUI(self):
        window = self.app  # Main window reference

        # Variable to store the download path
        export_path = tk.StringVar(value=os.path.join(os.getcwd(), "download"))
        # Variable to store the YouTube link
        youtubeLink = tk.StringVar(value="")
        # Variable to store the selected format
        selectedFormat = tk.StringVar(value="Video")

        # Function to select a folder for downloads
        def select_folder(event=None):
            folder_selected = filedialog.askdirectory()  # Open folder dialog
            if folder_selected:
                export_path.set(folder_selected)  # Update the selected folder path

        # Function to update YouTube link variable on key press
        def onLinkEntryKeyUp(event=None):
            youtubeLink.set(linkWiged.get())  # Update the link value

        # Function to validate YouTube link
        def validYouTubeLink(url: str):
            youtube_patterns = [
                r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$',  # Regular YouTube links
                r'(https?://)?(www\.)?youtube\.com/shorts/.+$',  # YouTube Shorts
                r'(https?://)?(music\.)?youtube\.com/.+$'  # YouTube Music
            ]
            for pattern in youtube_patterns:
                if re.match(pattern, url):
                    return True
            return False  # Invalid link if no patterns match

        # Function to reset the logger
        def ResetLogger():
            logger.configure(text="")  # Clear the displayed message

        # Function to update progress during download
        def ProgressLogger(target=None):
            if target is None or 'status' not in target:
                return
            if target['status'] == "downloading":
                downloaded_bytes = target.get('downloaded_bytes', 0)
                total_bytes = target.get('total_bytes', 0)
                percent = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                progress_text = f"Download progress: {percent:.2f}% ({downloaded_bytes / (1024 * 1024):.2f} MB of {total_bytes / (1024 * 1024):.2f} MB)"
                logger.configure(text=progress_text)
                logger.update_idletasks()
            elif target['status'] == "finished":
                logger.configure(text="Download successful.")
                logger.configure(text="Created by eng: Hossam Yosri.")
                window.after(3000, ResetLogger)
                self.isDownloading = False

        class NoLogger(object):
            def debug(self, _): pass
            def warning(self, _): pass
            def error(self, _): pass

        # Function to handle YouTube video or audio download
        def DownloadYouTube(event=None):
            if self.isDownloading:
                messagebox.showwarning("YouTube Downloader Alert", "Downloading, please wait")
                return

            def download_thread():
                self.isDownloading = True
                logger.configure(text="Fetching metadata from YouTube...")
                link = youtubeLink.get()
                out = export_path.get()
                isYoutubeLink = validYouTubeLink(link)

                if isYoutubeLink:
                    if not os.path.exists(out):
                        os.makedirs(out)
                    
                    try:
                        # Determine format based on user selection
                        if selectedFormat.get() == "Video":
                            ydl_opts = {
                                'format': 'best',
                                'progress_hooks': [ProgressLogger],
                                'outtmpl': os.path.join(out, '%(title)s.%(ext)s'),
                                'logger': NoLogger(),
                            }
                        elif selectedFormat.get() == "Audio":
                            ydl_opts = {
                                'format': 'bestaudio/best',
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '192',
                                }],
                                'progress_hooks': [ProgressLogger],
                                'outtmpl': os.path.join(out, '%(title)s.%(ext)s'),
                                'logger': NoLogger(),
                            }
                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([link])
                    except Exception as e:
                        logger.configure(text=f"Error: {str(e)}")
                    finally:
                        self.isDownloading = False
                else:
                    messagebox.showerror("Error", "Invalid YouTube URL")

            threading.Thread(target=download_thread).start()

        # UI Layout
        tk.CTkLabel(window, text="YouTube Downloader", font=("Arial", 16)).pack(pady=(10, 5))
        tk.CTkLabel(window, text="Select Export Folder:").pack(anchor="w", padx=20)
        tk.CTkEntry(window, textvariable=export_path, state="readonly").pack(fill="x", padx=20, pady=(5, 10))
        tk.CTkButton(window, text="Browse", command=select_folder).pack(pady=(0, 10))

        tk.CTkLabel(window, text="Enter YouTube URL:").pack(anchor="w", padx=20)
        linkWiged = tk.CTkEntry(window, textvariable=youtubeLink)
        linkWiged.pack(fill="x", padx=20, pady=(5, 10))
        linkWiged.bind("<KeyRelease>", onLinkEntryKeyUp)

        tk.CTkLabel(window, text="Select Format:").pack(anchor="w", padx=20)
        tk.CTkOptionMenu(window, values=["Video", "Audio"], variable=selectedFormat).pack(fill="x", padx=20, pady=(5, 10))

        tk.CTkButton(window, text="Download", command=DownloadYouTube).pack(pady=(10, 10))
        logger = tk.CTkLabel(window, text="", wraplength=400, font=("Arial", 10))
        logger.pack(pady=(5, 10))

        # Footer to display creator's name
        tk.CTkLabel(
            window, 
            text="Created by: Hossam Yosri", 
            font=("Arial", 18, "italic"), 
            anchor="center"
        ).pack(side="bottom", pady=9)

    def start(self):
        self.app.mainloop()

    def configure(self, options: ConfigureOption):
        self.app.title(options.get('name', "YouTube Downloader"))
        self.app.geometry(options.get('size', "450x420"))

if __name__ == "__main__":
    app = InitializeApplication(tk.CTk())
    app.configure({'name': 'YouTube Downloader'})
    app.start()
