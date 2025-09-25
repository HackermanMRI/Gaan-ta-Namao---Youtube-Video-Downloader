import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import os
import queue

from downloader import YouTubeDownloader
# We no longer need show_message from utils as it's not thread-safe

# Define a constant for the placeholder text to avoid errors
PLACEHOLDER_TEXT = "Paste URL here... (don't use shortened links)"

class FormatDialog(tk.Toplevel):
    """A modal dialog to select the download format and quality."""
    def __init__(self, parent, title, format_options, quality_options):
        super().__init__(parent)
        self.title(title)
        # self.geometry("350x200") # <-- REMOVED THIS LINE
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None
        
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=BOTH, expand=YES)
        main_frame.columnconfigure(0, weight=1)

        # --- Format Selection ---
        ttk.Label(main_frame, text="Please select a format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value=format_options[0])
        self.format_menu = ttk.Combobox(main_frame, textvariable=self.format_var, values=format_options, state="readonly")
        self.format_menu.grid(row=1, column=0, sticky="ew", pady=(5, 15))

        # --- Quality Selection ---
        ttk.Label(main_frame, text="Please select a quality:").grid(row=2, column=0, sticky="w")
        self.quality_var = tk.StringVar(value=quality_options[0])
        self.quality_menu = ttk.Combobox(main_frame, textvariable=self.quality_var, values=quality_options, state="readonly")
        self.quality_menu.grid(row=3, column=0, sticky="ew", pady=5)
        
        # --- Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky="ew", pady=(20, 0))
        button_frame.columnconfigure((0, 1), weight=1)
        ok_button = ttk.Button(button_frame, text="OK", command=self.ok_pressed, bootstyle="success")
        ok_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_pressed, bootstyle="secondary")
        cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def ok_pressed(self):
        file_format = self.format_var.get().split(" ")[0].lower()
        quality = self.quality_var.get()
        self.result = (file_format, quality)
        self.destroy()

    def cancel_pressed(self):
        self.result = None
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def ok_pressed(self):
        file_format = self.format_var.get().split(" ")[0].lower()
        quality = self.quality_var.get()
        self.result = (file_format, quality)
        self.destroy()

    def cancel_pressed(self):
        self.result = None
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result

class App(ttk.Window):
    """
    The main application class for the YouTube Downloader GUI.
    """
    def __init__(self):
        super().__init__()
        self.title("Gaan ta Namao")
        self.geometry("700x280")
        self.minsize(700, 280)
        self.resizable(True, True)
        self.info_frame = None
        self.available_resolutions = []
        self.available_bitrates = []
        self.ui_queue = queue.Queue()

        # --- Theme and Styling ---
        MAIN_THEME = "#9ECFF5"
        TEXT_BOX = "#D7E7F3"
        BUTTON = "#E4D8D0"
        BUTTON_SELECTED = "#57A4EC"
        BUTTON_HOVER = '#456882'
        PROGRESS_COLOR = '#D2C1B6'
        TEXT_COLOR = "#071D2C"
        BUTTON_TEXT = '#1B3C53'
        BUTTON_HOVER_TEXT = 'white'
        self.style.configure('.', background=MAIN_THEME, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        self.style.configure('TFrame', background=MAIN_THEME)
        self.style.configure('TLabel', background=MAIN_THEME, foreground=TEXT_COLOR)
        self.style.configure('TLabelframe', background=MAIN_THEME, bordercolor=TEXT_BOX)
        self.style.configure('TLabelframe.Label', background=MAIN_THEME, foreground=TEXT_COLOR, font=('Segoe UI', 12, 'bold'))
        self.style.configure('TEntry', fieldbackground=TEXT_BOX, foreground=TEXT_COLOR, bordercolor=TEXT_BOX, insertcolor=TEXT_COLOR)
        self.style.configure('TButton', background=BUTTON, foreground=BUTTON_TEXT, font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=5)
        self.style.map('TButton', background=[('active', BUTTON_HOVER), ('hover', BUTTON_HOVER)], foreground=[('active', BUTTON_HOVER_TEXT), ('hover', BUTTON_HOVER_TEXT)])
        self.style.configure('Toolbutton', background=TEXT_BOX, foreground=TEXT_COLOR, borderwidth=1, focusthickness=0, padding=8)
        self.style.map('Toolbutton', background=[('selected', BUTTON_SELECTED), ('hover', BUTTON_HOVER), ('active', BUTTON_HOVER)], foreground=[('selected', BUTTON_TEXT), ('hover', BUTTON_HOVER_TEXT), ('active', BUTTON_HOVER_TEXT)])
        self.style.configure('Success.TButton', background=BUTTON, foreground=BUTTON_TEXT)
        self.style.map('Success.TButton', background=[('active', BUTTON_HOVER), ('hover', BUTTON_HOVER), ('disabled', '#555')], foreground=[('active', BUTTON_HOVER_TEXT), ('hover', BUTTON_HOVER_TEXT)])
        self.style.configure('Striped.Horizontal.TProgressbar', troughcolor=TEXT_BOX, background=PROGRESS_COLOR)
        self.style.configure('Credit.TLabel', font=('Segoe UI', 7), foreground=BUTTON_TEXT)

        self.configure(bg=MAIN_THEME)
        self.downloader = YouTubeDownloader(self.update_progress)
        self._center_window()
        self.create_widgets()
        self._load_app_icon()
        self.after(100, self._process_queue)

    def _process_queue(self):
        try:
            while True:
                message = self.ui_queue.get_nowait()
                command, value = message
                if command == "update_status":
                    self.status_label.config(text=value)
                elif command == "update_title":
                    self.title_label.config(text=value)
                elif command == "update_progress":
                    self.progress_bar['value'] = value
                elif command == "set_button_state":
                    widget_name, state = value
                    if widget_name == 'fetch': self.fetch_button.config(state=state)
                    elif widget_name == 'download': self.download_button.config(state=state)
                elif command == "show_message":
                    title, msg = value
                    messagebox.showinfo(title, msg)
                elif command == "display_thumbnail":
                    self.thumbnail_image = ImageTk.PhotoImage(value)
                    self.thumbnail_label.config(image=self.thumbnail_image)
                elif command == "create_info_frame":
                    self._create_and_show_info_frame()
        except queue.Empty:
            self.after(100, self._process_queue)

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _load_app_icon(self):
        try:
            script_dir = os.path.dirname(__file__)
            logo_path = os.path.join(script_dir, "logo.png")
            img = Image.open(logo_path)
            self.logo_image = ImageTk.PhotoImage(img)
            self.iconphoto(True, self.logo_image)
        except Exception as e:
            print(f"Could not load app icon: {e}")

    def on_entry_click(self, event):
        if self.url_entry.get() == PLACEHOLDER_TEXT:
            self.url_entry.delete(0, "end")
            self.url_entry.config(foreground=self.style.lookup('TEntry', 'foreground'))

    def on_focusout(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, PLACEHOLDER_TEXT)
            self.url_entry.config(foreground='gray')

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.content_frame = ttk.Frame(self, padding="20")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=1)
        url_frame = ttk.Frame(self.content_frame)
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        url_frame.columnconfigure(0, weight=1)
        self.url_entry = ttk.Entry(url_frame, font=('Segoe UI', 11), width=60)
        self.url_entry.grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 10))
        self.url_entry.insert(0, PLACEHOLDER_TEXT)
        self.url_entry.config(foreground='gray')
        self.url_entry.bind('<FocusIn>', self.on_entry_click)
        self.url_entry.bind('<FocusOut>', self.on_focusout)
        self.fetch_button = ttk.Button(url_frame, text="Check", command=self.fetch_video_info)
        self.fetch_button.grid(row=0, column=1, sticky="e")
        bottom_controls_frame = ttk.Frame(self.content_frame)
        bottom_controls_frame.grid(row=2, column=0, sticky="ew")
        bottom_controls_frame.columnconfigure(0, weight=1)
        bottom_frame = ttk.Frame(bottom_controls_frame)
        bottom_frame.pack(fill=X, pady=10)
        bottom_frame.columnconfigure((0, 1), weight=1)
        self.download_type = tk.StringVar(value=None)
        video_btn = ttk.Radiobutton(bottom_frame, text="Video", variable=self.download_type, value="video", style='Toolbutton')
        video_btn.grid(row=0, column=0, sticky="ew", padx=(0,5))
        audio_btn = ttk.Radiobutton(bottom_frame, text="Audio", variable=self.download_type, value="audio", style='Toolbutton')
        audio_btn.grid(row=0, column=1, sticky="ew", padx=(5,0))
        self.download_button = ttk.Button(bottom_controls_frame, text="Download", state="disabled", command=self.start_download, style='Success.TButton')
        self.download_button.pack(fill=X, ipady=5, pady=(5, 10))
        self.progress_bar = ttk.Progressbar(bottom_controls_frame, mode="determinate", style='Striped.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=X, pady=5, ipady=2)
        footer_frame = ttk.Frame(self)
        footer_frame.grid(row=1, column=0, sticky="e", padx=10, pady=(0, 5))
        credit_label = ttk.Label(footer_frame, text="Developed by Mrinmoy  |  For any feedback : mrinmoylax01@gmail.com ", style='Credit.TLabel', font=('Arial', 7))
        credit_label.pack() 

    def _create_and_show_info_frame(self):
        if self.info_frame is not None: return
        self.info_frame = ttk.LabelFrame(self.content_frame, text="Video Information", padding="15")
        self.info_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.rowconfigure(1, weight=1)
        if self.winfo_height() < 550:
            self.geometry(f"700x550")
            self._center_window()
        placeholder = Image.new('RGB', (240, 135), color="#F6FDFF")
        self.thumbnail_image = ImageTk.PhotoImage(placeholder)
        self.thumbnail_label = ttk.Label(self.info_frame, image=self.thumbnail_image)
        self.thumbnail_label.grid(row=0, column=0, pady=5)
        self.title_label = ttk.Label(self.info_frame, text="Video title will appear here.", font=('Segoe UI', 11, 'bold'), wraplength=600, justify="center", anchor="center")
        self.title_label.grid(row=1, column=0, sticky="nsew", pady=10)
        self.status_label = ttk.Label(self.info_frame, text="...", font=('Segoe UI', 9), justify="center", anchor="center")
        self.status_label.grid(row=2, column=0, sticky="ew", pady=5)

    def fetch_video_info(self):
        url = self.url_entry.get()
        if not url or url == PLACEHOLDER_TEXT:
            self.ui_queue.put(("show_message", ("Error", "Please enter a valid YouTube URL.")))
            return
        if self.info_frame:
            self.ui_queue.put(("update_status", "Fetching video information..."))
        self.ui_queue.put(("set_button_state", ('fetch', 'disabled')))
        self.ui_queue.put(("set_button_state", ('download', 'disabled')))
        threading.Thread(target=self._fetch_video_info_thread, args=(url,), daemon=True).start()

    def _fetch_video_info_thread(self, url):
        try:
            video_info = self.downloader.get_video_info(url)
            self.available_resolutions = video_info.get('video_resolutions', [])
            self.available_bitrates = video_info.get('audio_bitrates', [])
            self.ui_queue.put(("create_info_frame", None))
            self.ui_queue.put(("update_title", video_info['title']))
            self.display_thumbnail(video_info['thumbnail_url'])
            self.ui_queue.put(("set_button_state", ('download', 'normal')))
            self.ui_queue.put(("update_status", "Select Audio/Video then hit Download."))
        except Exception as e:
            self.ui_queue.put(("create_info_frame", None))
            self.ui_queue.put(("show_message", ("Error", f"Failed to fetch video info: {e}")))
            self.ui_queue.put(("update_status", "Error fetching info."))
        finally:
            self.ui_queue.put(("set_button_state", ('fetch', 'normal')))

    def display_thumbnail(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img.thumbnail((240, 135))
            self.ui_queue.put(("display_thumbnail", img))
        except Exception as e:
            print(f"Could not load thumbnail: {e}")

    def start_download(self):
        download_type = self.download_type.get()
        if not download_type:
            self.ui_queue.put(("show_message", ("Error", "Please select a download format (Video or Audio).")))
            return

        if download_type == 'video':
            format_options = ['MP4 (Recommended)', 'MOV', 'AVI', 'MKV']
            quality_options = self.available_resolutions if self.available_resolutions else ['Default']
            dialog_title = "Select Video Options"
        else: # audio
            format_options = ['MP3 (Recommended)', 'WAV', 'M4A', 'AAC']
            quality_options = self.available_bitrates if self.available_bitrates else ['Default']
            dialog_title = "Select Audio Options"

        dialog = FormatDialog(self, title=dialog_title, format_options=format_options, quality_options=quality_options)
        result = dialog.show()

        if not result: return
        file_format, quality = result

        save_path = filedialog.askdirectory()
        if not save_path: return

        self.ui_queue.put(("set_button_state", ('download', 'disabled')))
        self.ui_queue.put(("set_button_state", ('fetch', 'disabled')))
        self.ui_queue.put(("update_progress", 0))
        self.ui_queue.put(("update_status", "Starting download..."))
        threading.Thread(target=self._download_thread, args=(download_type, save_path, file_format, quality), daemon=True).start()

    def _download_thread(self, download_type, save_path, file_format, quality):
        try:
            if download_type == "video":
                self.downloader.download_video(save_path, video_format=file_format, resolution=quality)
            else:
                self.downloader.download_audio(save_path, audio_format=file_format, bitrate=quality)
            self.ui_queue.put(("update_status", "Download completed successfully! 🎉"))
            self.ui_queue.put(("show_message", ("Success", f"{download_type.capitalize()} downloaded successfully!")))
        except Exception as e:
            self.ui_queue.put(("update_status", "Download failed."))
            self.ui_queue.put(("show_message", ("Error", f"An error occurred: {e}")))
        finally:
            self.ui_queue.put(("update_progress", 0))
            self.ui_queue.put(("set_button_state", ('download', 'normal')))
            self.ui_queue.put(("set_button_state", ('fetch', 'normal')))

    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.ui_queue.put(("update_progress", percentage))
        self.ui_queue.put(("update_status", f"Downloading... {int(percentage)}%"))

if __name__ == "__main__":
    app = App()
    app.mainloop()

