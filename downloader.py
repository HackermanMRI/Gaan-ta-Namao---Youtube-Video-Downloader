from pytubefix import YouTube
import os
import subprocess

class YouTubeDownloader:
    """
    Handles the logic for downloading video and audio from YouTube.
    Uses subprocess to call ffmpeg for audio conversion, removing the
    need for the moviepy library.
    """
    def __init__(self, progress_callback=None):
        """
        Initializes the downloader.
        :param progress_callback: A function to call to update download progress.
        """
        self.yt = None
        self.video_stream = None
        self.audio_stream = None
        self.progress_callback = progress_callback

    def get_video_info(self, url):
        """
        Retrieves video information for a given YouTube URL.
        :param url: The YouTube video URL.
        :return: A dictionary with video title and thumbnail URL.
        """
        self.yt = YouTube(url, on_progress_callback=self.progress_callback)

        # Get the best progressive stream (video + audio)
        self.video_stream = self.yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        # Get the best audio-only stream
        self.audio_stream = self.yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        if not self.video_stream and not self.audio_stream:
            raise ConnectionError("No downloadable streams found for this video.")

        return {
            'title': self.yt.title,
            'thumbnail_url': self.yt.thumbnail_url
        }

    def download_video(self, save_path):
        """
        Downloads the selected video stream.
        :param save_path: The directory where the video will be saved.
        """
        if not self.video_stream:
            raise ValueError("Video stream not available. Fetch video info first.")

        print(f"Downloading video: {self.yt.title}")
        self.video_stream.download(output_path=save_path)
        print("Video download completed.")

    def download_audio(self, save_path):
        """
        Downloads the audio stream and converts it to MP3 using ffmpeg.
        :param save_path: The directory where the audio will be saved.
        """
        if not self.audio_stream:
            raise ValueError("Audio stream not available. Fetch video info first.")

        print(f"Downloading audio for: {self.yt.title}")
        # Download the audio stream (usually in .mp4 format)
        temp_file = self.audio_stream.download(output_path=save_path)
        
        # --- NEW CONVERSION LOGIC ---
        base, ext = os.path.splitext(temp_file)
        mp3_file = base + '.mp3'
        
        # Construct the ffmpeg command
        # -i: input file
        # -y: overwrite output file if it exists
        # -loglevel error: only show errors
        command = [
            'ffmpeg',
            '-i', temp_file,
            '-y',
            '-loglevel', 'error',
            mp3_file
        ]

        try:
            print("Converting to MP3 using ffmpeg...")
            subprocess.run(command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Conversion to MP3 completed.")
        except FileNotFoundError:
            raise SystemError("ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg conversion failed: {e}")
        finally:
            # Remove the original downloaded audio file
            if os.path.exists(temp_file):
                os.remove(temp_file)

