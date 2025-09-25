import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import os

from downloader import YouTubeDownloader
from utils import show_message

# Define a constant for the placeholder text to avoid errors
PLACEHOLDER_TEXT = "Paste URL here... (don't use shortened links)"

class App(ttk.Window):
    """
    The main application class for the YouTube Downloader GUI,
    redesigned with a custom modern, light theme.
    """
    def __init__(self):
        super().__init__()
        self.title("Gaan ta Namao")
        # Start with a compact window size
        self.geometry("700x280")
        self.resizable(False, False)
        self.info_frame = None # This will hold the info frame when created

        # --- Create Custom Theme from User Palette ---
        MAIN_THEME = "#9ECFF5"
        TEXT_BOX = "#D7E7F3"
        BUTTON = "#E4D8D0"
        BUTTON_SELECTED = "#57A4EC"
        BUTTON_HOVER = '#456882'
        PROGRESS_COLOR = '#D2C1B6'
        TEXT_COLOR = "#071D2C"
        BUTTON_TEXT = '#1B3C53'
        BUTTON_HOVER_TEXT = 'white'

        # Configure styles for all widgets
        self.style.configure('.', background=MAIN_THEME, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        self.style.configure('TFrame', background=MAIN_THEME)
        self.style.configure('TLabel', background=MAIN_THEME, foreground=TEXT_COLOR)
        self.style.configure('TLabelframe', background=MAIN_THEME, bordercolor=TEXT_BOX)
        self.style.configure('TLabelframe.Label', background=MAIN_THEME, foreground=TEXT_COLOR, font=('Segoe UI', 12, 'bold'))

        self.style.configure('TEntry', fieldbackground=TEXT_BOX, foreground=TEXT_COLOR, bordercolor=TEXT_BOX, insertcolor=TEXT_COLOR)
        
        self.style.configure('TButton', background=BUTTON, foreground=BUTTON_TEXT, font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=5)
        self.style.map('TButton',
            background=[('active', BUTTON_HOVER), ('hover', BUTTON_HOVER)],
            foreground=[('active', BUTTON_HOVER_TEXT), ('hover', BUTTON_HOVER_TEXT)]
        )

        self.style.configure('Toolbutton', background=TEXT_BOX, foreground=TEXT_COLOR, borderwidth=1, focusthickness=0, padding=8)
        self.style.map('Toolbutton',
            background=[('selected', BUTTON_SELECTED), ('hover', BUTTON_HOVER), ('active', BUTTON_HOVER)],
            foreground=[('selected', BUTTON_TEXT), ('hover', BUTTON_HOVER_TEXT), ('active', BUTTON_HOVER_TEXT)]
        )

        self.style.configure('Success.TButton', background=BUTTON, foreground=BUTTON_TEXT)
        self.style.map('Success.TButton',
            background=[('active', BUTTON_HOVER), ('hover', BUTTON_HOVER), ('disabled', '#555')],
            foreground=[('active', BUTTON_HOVER_TEXT), ('hover', BUTTON_HOVER_TEXT)]
        )
        
        self.style.configure('Striped.Horizontal.TProgressbar', troughcolor=TEXT_BOX, background=PROGRESS_COLOR)

        # Style for the developer credit label
        self.style.configure('Credit.TLabel', font=('Segoe UI', 7), foreground=BUTTON_TEXT)

        self.configure(bg=MAIN_THEME)

        self.downloader = YouTubeDownloader(self.update_progress)
        self.create_widgets()

        # Load the app icon from local storage
        self._load_app_icon()

    def _load_app_icon(self):
        """Loads the application icon from a local file named 'logo.png'."""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(__file__)
            # Join the directory with the filename to get the full path
            logo_path = os.path.join(script_dir, "logo.png")
            
            img = Image.open(logo_path)
            self.logo_image = ImageTk.PhotoImage(img)
            self.iconphoto(True, self.logo_image)
        except FileNotFoundError:
            print("Logo file not found: Please make sure 'logo.png' is in the same directory as main.py.")
        except Exception as e:
            print(f"Could not load app icon: {e}")

    def on_entry_click(self, event):
        """Called when the URL entry box is clicked."""
        if self.url_entry.get() == PLACEHOLDER_TEXT:
            self.url_entry.delete(0, "end")
            self.url_entry.config(foreground=self.style.lookup('TEntry', 'foreground'))

    def on_focusout(self, event):
        """Called when the URL entry box loses focus."""
        if not self.url_entry.get():
            self.url_entry.insert(0, PLACEHOLDER_TEXT)
            self.url_entry.config(foreground='gray')

    def create_widgets(self):
        """Creates and arranges the widgets in the main window."""
        
        # --- Footer Frame for Developer Credit (Packed to the bottom of the main window) ---
        footer_frame = ttk.Frame(self)
        footer_frame.pack(side=BOTTOM, fill=X, padx=10, pady=(0, 5))
        credit_label = ttk.Label(footer_frame, text="@ Developed by Mrinmoy", style='Credit.TLabel')
        credit_label.pack(side=RIGHT)

        # --- Content Frame for all other widgets (Takes up all remaining space) ---
        self.content_frame = ttk.Frame(self, padding="20")
        self.content_frame.pack(side=TOP, fill=BOTH, expand=YES)

        # --- URL Frame ---
        url_frame = ttk.Frame(self.content_frame)
        url_frame.pack(fill=X, pady=(0, 20))
        url_frame.columnconfigure(0, weight=1)

        self.url_entry = ttk.Entry(url_frame, font=('Segoe UI', 11), width=60)
        self.url_entry.grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 10))
        self.url_entry.insert(0, PLACEHOLDER_TEXT)
        self.url_entry.config(foreground='gray')
        self.url_entry.bind('<FocusIn>', self.on_entry_click)
        self.url_entry.bind('<FocusOut>', self.on_focusout)

        self.fetch_button = ttk.Button(url_frame, text="Check", command=self.fetch_video_info)
        self.fetch_button.grid(row=0, column=1, sticky="e")
        
        # --- Options & Download Frame (created before info box appears) ---
        self.bottom_frame = ttk.Frame(self.content_frame)
        self.bottom_frame.pack(fill=X, pady=10)
        self.bottom_frame.columnconfigure((0, 1), weight=1)

        self.download_type = tk.StringVar(value=None)
        video_btn = ttk.Radiobutton(self.bottom_frame, text="Video", variable=self.download_type, value="video", style='Toolbutton')
        video_btn.grid(row=0, column=0, sticky="ew", padx=(0,5))
        audio_btn = ttk.Radiobutton(self.bottom_frame, text="Audio", variable=self.download_type, value="audio", style='Toolbutton')
        audio_btn.grid(row=0, column=1, sticky="ew", padx=(5,0))
        
        self.download_button = ttk.Button(self.content_frame, text="Download", state="disabled", command=self.start_download, style='Success.TButton')
        self.download_button.pack(fill=X, ipady=5, pady=(0, 0))

        self.progress_bar = ttk.Progressbar(self.content_frame, mode="determinate", style='Striped.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=X, pady=5, ipady=2)

    def _create_and_show_info_frame(self):
        """Creates the info frame widget if it doesn't exist and displays it."""
        if self.info_frame is not None:
            return  # Don't create it again if it already exists

        # --- Info Frame ---
        self.info_frame = ttk.LabelFrame(self.content_frame, text="Video Information", padding="15")
        self.info_frame.pack(fill=BOTH, expand=YES, pady=(0, 20), before=self.bottom_frame)
        
        # Expand the window to the full size
        self.geometry("700x550")

        placeholder = Image.new('RGB', (320, 180), color="#F6FDFF")
        self.thumbnail_image = ImageTk.PhotoImage(placeholder)
        self.thumbnail_label = ttk.Label(self.info_frame, image=self.thumbnail_image)
        self.thumbnail_label.pack(pady=5)

        self.title_label = ttk.Label(self.info_frame, text="Video title will appear here.", font=('Segoe UI', 12, 'bold'), wraplength=600, justify="center", anchor="center")
        self.title_label.pack(pady=10, fill=X, expand=YES)
        
        self.status_label = ttk.Label(self.info_frame, text="...", font=('Segoe UI', 9), justify="center", anchor="center")
        self.status_label.pack(pady=5, fill=X, expand=YES)

    def fetch_video_info(self):
        url = self.url_entry.get()
        if not url or url == PLACEHOLDER_TEXT:
            show_message("Error", "Please enter a valid YouTube URL.")
            return
        
        # If the info frame already exists, reset its status label
        if self.info_frame:
            self.status_label.config(text="Fetching video information...")
            
        self.fetch_button.config(state="disabled")
        self.download_button.config(state="disabled")
        threading.Thread(target=self._fetch_video_info_thread, args=(url,), daemon=True).start()

    def _fetch_video_info_thread(self, url):
        try:
            video_info = self.downloader.get_video_info(url)
            self._create_and_show_info_frame()
            self.title_label.config(text=video_info['title'])
            self.display_thumbnail(video_info['thumbnail_url'])
            self.download_button.config(state="normal")
            self.status_label.config(text="Select your download format")
        except Exception as e:
            self._create_and_show_info_frame()
            show_message("Error", f"Failed to fetch video info: {e}")
            self.status_label.config(text="Error fetching info.")
        finally:
            self.fetch_button.config(state="normal")

    def display_thumbnail(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img.thumbnail((320, 180))
            self.thumbnail_image = ImageTk.PhotoImage(img)
            self.thumbnail_label.config(image=self.thumbnail_image)
        except Exception as e:
            print(f"Could not load thumbnail: {e}")
            self.status_label.config(text="Could not load thumbnail.")

    def start_download(self):
        download_type = self.download_type.get()
        if not download_type:
            show_message("Error", "Please select a download format (Video or Audio).")
            return
            
        save_path = filedialog.askdirectory()
        if not save_path:
            return
        self.download_button.config(state="disabled")
        self.fetch_button.config(state="disabled")
        self.progress_bar['value'] = 0
        self.status_label.config(text=f"Starting download...")
        threading.Thread(target=self._download_thread, args=(download_type, save_path), daemon=True).start()

    def _download_thread(self, download_type, save_path):
        try:
            if download_type == "video":
                self.downloader.download_video(save_path)
            else:
                self.downloader.download_audio(save_path)
            self.status_label.config(text="Download completed successfully! 🎉")
            show_message("Success", f"{download_type.capitalize()} downloaded successfully!")
        except Exception as e:
            self.status_label.config(text="Download failed.")
            show_message("Error", f"An error occurred: {e}")
        finally:
            self.progress_bar['value'] = 0
            self.download_button.config(state="normal")
            self.fetch_button.config(state="normal")

    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar['value'] = percentage
        self.status_label.config(text=f"Downloading... {int(percentage)}%")
        self.update_idletasks()


if __name__ == "__main__":
    app = App()
    app.mainloop()

