import os ,re,sys,threading
import customtkinter as tk
from typing import TypedDict
from yt_dlp import YoutubeDL
from tkinter import filedialog, messagebox
from PIL import Image
import requests

# Function to get the correct path for bundled files when using PyInstaller
def resource_path(relative_path):
    try:
        # When running as a bundled executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running the script directly
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set default theme using 'theme.json'
tk.set_default_color_theme(resource_path('C:/Users/Hossam/Downloads/V3/theme.json'))

# Define a structure for application settings
class ConfigureOption(TypedDict):
    name: str  # App name
    size: str  # Window size

# Main class to initialize the application
class InitializeApplication:

    def __init__(self, app: tk.CTk):
        self.app = app  # Assign app instance
        self.isDownloading = False  # Download status flag
        self.createApplicationUI()  # Create UI components

    def createApplicationUI(self):
        window = self.app  # Main window reference

        # Variable to store the download path
        export_path = tk.StringVar(value=os.path.join(os.getcwd(), "download"))
        # Variable to store the input link
        input_link = tk.StringVar(value="")
        # Variable to store the selected format
        selectedFormat = tk.StringVar(value="")

        # Function to select a folder for downloads
        def select_folder(event=None):
            folder_selected = filedialog.askdirectory()  # Open folder dialog
            if folder_selected:
                export_path.set(folder_selected)  # Update the selected folder path

        # Function to update the input link variable on key press
        def onLinkEntryKeyUp(event=None):
            input_link.set(linkWidget.get())  # Update the link value

        # Function to validate the input link
        def valid_input_link(url: str):
            # Patterns to match video and image platforms
            patterns = [
                r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$',  # YouTube
                r'(https?://)?(www\.)?(facebook\.com|fb\.watch)/.+$',  # Facebook
                r'(https?://)?(www\.)?instagram\.com/.+$',  # Instagram
                r'(https?://)?(www\.)?twitter\.com/.+$',  # Twitter
                r'(https?://)?(www\.)?tiktok\.com/.+$',  # TikTok
                r'(https?://)?.+\.(jpg|jpeg|png|gif|hice|ico)$'  # Direct image links
            ]
            for pattern in patterns:
                if re.match(pattern, url):
                    return True
            return False  # Invalid link if no patterns match

        # Function to reset the logger
        def reset_logger():
            logger.configure(text="")  # Clear the displayed message

        # Function to update progress during download
        def progress_logger(target=None):
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
                window.after(3000, reset_logger)
                self.isDownloading = False

        # Function to download images
        def download_image(link, output_path):
            try:
                response = requests.get(link, stream=True)
                if response.status_code == 200:
                    file_name = os.path.join(output_path, link.split("/")[-1])
                    with open(file_name, 'wb') as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    logger.configure(text="Image downloaded successfully.")
                else:
                    logger.configure(text="Failed to download image.")
            except Exception as e:
                logger.configure(text=f"Error: {str(e)}")

        # Function to handle video/audio/image downloads
        def download_content(event=None):
            if self.isDownloading:
                messagebox.showwarning("Downloader Alert", "Downloading, please wait")
                return

            def download_thread():
                self.isDownloading = True
                logger.configure(text="Processing your request...")
                link = input_link.get()
                out = export_path.get()
                is_valid_link = valid_input_link(link)

                if is_valid_link:
                    if not os.path.exists(out):
                        os.makedirs(out)

                    try:
                        # Handle image downloads
                        if selectedFormat.get() == "Image":
                            download_image(link, out)

                        # Handle video/audio downloads
                        else:
                            ydl_opts = {}
                            if selectedFormat.get() == "Video":
                                ydl_opts = {
                                    'format': 'best',
                                    'progress_hooks': [progress_logger],
                                    'outtmpl': os.path.join(out, '%(title)s.%(ext)s')
                                }
                            elif selectedFormat.get() == "Audio":
                                ydl_opts = {
                                    'format': 'bestaudio/best',
                                    'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '192',
                                    }],
                                    'progress_hooks': [progress_logger],
                                    'outtmpl': os.path.join(out, '%(title)s.%(ext)s')
                                }
                            with YoutubeDL(ydl_opts) as ydl:
                                ydl.download([link])
                    except Exception as e:
                        logger.configure(text=f"Error: {str(e)}")
                    finally:
                        self.isDownloading = False
                else:
                    messagebox.showerror("Error", "Invalid URL")

            threading.Thread(target=download_thread).start()

        # UI Layout
        tk.CTkLabel(window, text="Multi-Platform Downloader", font=("Arial", 16)).pack(pady=(10, 5))
        tk.CTkLabel(window, text="Select Export Folder:").pack(anchor="w", padx=20)
        tk.CTkEntry(window, textvariable=export_path, state="readonly").pack(fill="x", padx=20, pady=(5, 10))
        tk.CTkButton(window, text="Browse", command=select_folder).pack(pady=(0, 10))

        tk.CTkLabel(window, text="Enter URL:").pack(anchor="w", padx=20)
        linkWidget = tk.CTkEntry(window, textvariable=input_link)
        linkWidget.pack(fill="x", padx=20, pady=(5, 10))
        linkWidget.bind("<KeyRelease>", onLinkEntryKeyUp)

        tk.CTkLabel(window, text="Select Format:").pack(anchor="w", padx=20)
        tk.CTkOptionMenu(window, values=["Video", "Audio", "Image"], variable=selectedFormat).pack(fill="x", padx=20, pady=(5, 10))

        tk.CTkButton(window, text="Download", command=download_content).pack(pady=(10, 10))
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
        self.app.title(options.get('name', "Multi-Platform Downloader"))
        self.app.geometry(options.get('size', "450x500"))

if __name__ == "__main__":
    app = InitializeApplication(tk.CTk())
    app.configure({'name': 'Multi-Platform Downloader', 'size': '500x550'})
    app.start()
