# YouTube Channel URL Extractor

A lightweight Python tool that extracts the latest video URL from a YouTube channel or a custom playlist, **only if the video was published *today***. If there are no new videos published today, it safely returns nothing or alerts the user.

## Features
- **Supports Both Formats**: Works seamlessly with YouTube Channel URLs (e.g., `/@YouTube`) and Custom Playlist URLs (e.g., `/playlist?list=...`).
- **Robust Playlist Parsing**: Automatically checks both the beginning and the end of the lists. This is meant to catch new videos whether the playlist is sorted chronological or reverse-chronological.
- **Accurate Verification**: Bypasses the limitations of `yt-dlp`'s fast playlist extraction (which often misses true `upload_date` values) by querying detailed metadata for candidate videos to prevent false negatives.

## Prerequisites
- Python 3.x
- Virtual Environment (`venv`)

## Installation

Create the virtual environment and install the required packages (e.g., `yt-dlp`):

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment (Windows)
.\venv\Scripts\Activate.ps1
# Or for Command Prompt:
# venv\Scripts\activate.bat

# 3. Install requirements
pip install -r requirements.txt
```

## Usage

### Method 1: Using the Python CLI
You can pass the target URL directly as an argument to the python script:
```bash
# For a Channel
python main.py "https://www.youtube.com/@YouTube"

# For a Playlist
python main.py "https://www.youtube.com/playlist?list=PLVu0pIxQ7F-yvxR_dCP_zBgChK3s84b99"
```

### Method 2: Using the Windows Batch File (`extract.bat`)
For quick execution without opening a terminal every time:
1. Open `extract.bat` with any text editor (like Notepad).
2. Modify the `CHANNEL_URL` variable to your desired YouTube URL:
   ```bat
   set CHANNEL_URL=https://www.youtube.com/playlist?list=PLVu0pIxQ7F-yvxR_dCP...
   ```
3. Save the file.
4. Simply double-click `extract.bat` in Windows File Explorer to run it. The window will pause at the end so you can view the output nicely.

## How It Works
To remain fast while providing accurate dates without getting blocked by YouTube:
1. The script first fetches the "flat" structure of the entire playlist (~1-2 seconds).
2. It slices the top 5 and bottom 5 videos as "candidates."
3. It selectively fetches detailed metadata (which contains verified `upload_date`) only for these candidates until it finds a match for today's date.
