from pytubefix import YouTube
import os
import subprocess

class YouTubeDownloader:
    """
    Handles the logic for downloading and converting video and audio from YouTube.
    """
    def __init__(self, progress_callback=None):
        self.yt = None
        self.progress_callback = progress_callback

    def get_video_info(self, url):
        self.yt = YouTube(url, on_progress_callback=self.progress_callback)

        # --- Get Available Video Resolutions ---
        video_streams = self.yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
        resolutions = sorted(list(set([s.resolution for s in video_streams if s.resolution])), key=lambda x: int(x.replace('p', '')), reverse=True)

        # --- Get Available Audio Bitrates ---
        audio_streams = self.yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc()
        bitrates = sorted(list(set([s.abr for s in audio_streams if s.abr])), key=lambda x: int(x.replace('kbps', '')), reverse=True)
        
        if not resolutions and not bitrates:
            raise ConnectionError("No downloadable streams found for this video.")

        return {
            'title': self.yt.title,
            'thumbnail_url': self.yt.thumbnail_url,
            'video_resolutions': resolutions,
            'audio_bitrates': bitrates
        }

    def _sanitize_filename(self, filename):
        """Removes characters that are invalid for filenames."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename

    def _get_unique_filename(self, file_path):
        """
        Checks if a file exists and returns a unique name by appending (1), (2), etc.
        """
        if not os.path.exists(file_path):
            return file_path

        directory, filename = os.path.split(file_path)
        name, extension = os.path.splitext(filename)

        counter = 1
        while True:
            new_filename = f"{name} ({counter}){extension}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def download_video(self, save_path, resolution, video_format='mp4'):
        print(f"Attempting to download video at {resolution}...")
        
        # Select the appropriate video stream
        video_stream = self.yt.streams.filter(res=resolution, file_extension='mp4', progressive=True).first()
        is_progressive = True
        if not video_stream:
            # If no progressive stream, find an adaptive (video-only) stream
            video_stream = self.yt.streams.filter(res=resolution, file_extension='mp4', adaptive=True).first()
            is_progressive = False

        if not video_stream:
            raise ValueError(f"No video stream found for resolution: {resolution}")
        
        sanitized_title = self._sanitize_filename(self.yt.title)
        
        if is_progressive:
            print("Downloading progressive stream...")
            temp_file = video_stream.download(output_path=save_path, filename=f"{sanitized_title}_temp.mp4")
            
            # Define the initial desired output file path
            initial_output_file = os.path.join(save_path, f"{sanitized_title}.{video_format}")
            final_output_file = self._get_unique_filename(initial_output_file)

            if video_format != 'mp4':
                self._run_ffmpeg_conversion(temp_file, final_output_file)
            else:
                os.rename(temp_file, final_output_file)
        else:
            print("Downloading adaptive streams (video and audio)...")
            video_temp = video_stream.download(output_path=save_path, filename=f"{sanitized_title}_vid.mp4")
            
            audio_stream = self.yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            audio_temp = audio_stream.download(output_path=save_path, filename=f"{sanitized_title}_aud.mp4")
            
            initial_output_file = os.path.join(save_path, f"{sanitized_title}.{video_format}")
            final_output_file = self._get_unique_filename(initial_output_file)
            
            self._run_ffmpeg_merge(video_temp, audio_temp, final_output_file)

    def download_audio(self, save_path, bitrate, audio_format='mp3'):
        print(f"Attempting to download audio at {bitrate}...")
        audio_stream = self.yt.streams.filter(abr=bitrate, only_audio=True, file_extension='mp4').first()

        if not audio_stream:
            raise ValueError(f"No audio stream found for bitrate: {bitrate}")

        sanitized_title = self._sanitize_filename(self.yt.title)
        temp_file = audio_stream.download(output_path=save_path, filename=f"{sanitized_title}_temp.mp4")
        
        initial_output_file = os.path.join(save_path, f"{sanitized_title}.{audio_format}")
        final_output_file = self._get_unique_filename(initial_output_file)

        self._run_ffmpeg_conversion(temp_file, final_output_file)

    def _run_ffmpeg_conversion(self, input_file, output_file):
        """Runs a simple ffmpeg conversion and cleans up the input file."""
        command = ['ffmpeg', '-i', input_file, '-y', '-loglevel', 'error', output_file]
        try:
            print(f"Converting '{input_file}' to '{output_file}'...")
            subprocess.run(command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Conversion completed.")
        except FileNotFoundError:
            raise SystemError("ffmpeg not found. Please ensure it is installed and in your system's PATH.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg conversion failed: {e}")
        finally:
            if os.path.exists(input_file):
                os.remove(input_file)

    def _run_ffmpeg_merge(self, video_file, audio_file, output_file):
        """Merges a video and audio file using ffmpeg and cleans up."""
        command = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy', # Copy video stream without re-encoding
            '-c:a', 'aac',  # Re-encode audio to AAC (standard for mp4)
            '-strict', 'experimental',
            '-y',
            '-loglevel', 'error',
            output_file
        ]
        try:
            print(f"Merging video and audio to '{output_file}'...")
            subprocess.run(command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Merge completed.")
        except FileNotFoundError:
            raise SystemError("ffmpeg not found. Please ensure it is installed and in your system's PATH.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg merge failed: {e}")
        finally:
            if os.path.exists(video_file):
                os.remove(video_file)
            if os.path.exists(audio_file):
                os.remove(audio_file)

