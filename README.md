Gaan ta Namao - A Sleek YouTube Downloader
@ Developed by Mrinmoy
CSE, Jagannath University

"Gaan ta Namao" is a sleek and user-friendly desktop application designed to effortlessly download your favorite YouTube content. With a beautiful, custom-themed interface, it allows you to save any YouTube video directly to your computer or convert it into a high-quality MP3 audio file with just a few clicks.

Screenshot
The clean and modern user interface of Gaan ta Namao.

Features
Download YouTube Videos: Save videos in MP4 format.

Convert to MP3: Extract and convert the audio from any video into an MP3 file.

Sleek User Interface: A beautiful, custom-built light theme that is easy on the eyes.

Dynamic UI: The interface remains clean and compact until a video link is checked, at which point it expands to show the video details.

Simple to Use: Just paste a link, choose a format, and download.

Progress Tracking: A visual progress bar shows the real-time status of your download.

Installation
For End-Users
The easiest way to get started is to download the latest installer.

Go to the Releases page of this repository.

Download the Gaan_ta_Namao_Setup.exe file from the latest release.

Run the installer and follow the on-screen instructions. The application will be added to your Windows Start Menu.

For Developers
If you want to run the application from the source code, follow these steps:

1. Prerequisites:

You must have Python 3.8 or newer installed.

You must have FFmpeg installed and accessible in your system's PATH. This is crucial for audio conversion.

2. Clone the Repository:

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

3. Set Up a Virtual Environment:

# Create the environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\activate

4. Install Dependencies:
The required libraries are listed in requirements.txt.

pip install -r requirements.txt

(Note: You will need to create a requirements.txt file containing the following lines:)

ttkbootstrap
Pillow
requests
pytubefix

5. Run the Application:

python main.py

Building from Source
If you want to package the application into an executable (.exe) and create an installer, you will need two additional tools.

Install Build Tools:

pip install pyinstaller

Download and Install Inno Setup: https://jrsoftware.org/isinfo.php

Build the Executable:
Run the following command from the project root to create a single .exe file in the dist folder.

pyinstaller --name "Gaan ta Namao" --windowed --onefile --add-data "logo.png;." --add-binary "ffmpeg.exe;." --icon="logo.ico" main.py
