# YouTube Channel URL Extractor

A lightweight Python tool that extracts the latest video URL from a YouTube channel or a custom playlist, **only if the video was published *today***. If there are no new videos published today, it safely returns nothing or alerts the user.

## Motivation & Use Case
The primary goal of this project is to serve as the critical first step in a **local YouTube transcription & summarization pipeline**.

**Why is this necessary?** 
Many YouTube creators do not enable the platform's built-in transcription feature, making it impossible to directly scrape closed captions. While various third-party online tools offer transcription services, they typically require paid subscriptions.

If you have a local machine capable of running LLMs (e.g. your own GPU running **Whisper**), you can bypass these paid services entirely. By automatically extracting a channel's newly published video URL via this script, you can seamlessly feed it into the following automated pipeline:
1. Automatically download the audio track via `yt-dlp`.
2. Generate an accurate, cost-free local transcript via Whisper / WhisperX.
3. Feed the resulting text directly into a locally hosted LLM or APIs (like GPT-4) for daily summarization or insights extraction.

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

# Download audio if a new video is found today
python main.py "https://www.youtube.com/@YouTube" -d
```

### Method 2: Using the Windows Batch File (`extract.bat`)
For quick execution without opening a terminal every time:
1. Open `extract.bat` with any text editor (like Notepad).
2. Modify the `CHANNEL_URL` variable to your desired YouTube URL:
   ```bat
   set CHANNEL_URL=https://www.youtube.com/playlist?list=PLVu0pIxQ7F-yvxR_dCP...
   ```
3. Save the file.
4. Simply double-click `extract.bat` in Windows File Explorer to run it. The window will pause at the end so you can view the output nicely. (Alternatively, run `extract.bat -d` from a terminal to download the audio automatically).

## How It Works
To remain fast while providing accurate dates without getting blocked by YouTube:
1. The script first fetches the "flat" structure of the entire playlist (~1-2 seconds).
2. It slices the top 5 and bottom 5 videos as "candidates."
3. It selectively fetches detailed metadata (which contains verified `upload_date`) only for these candidates until it finds a match for today's date.

## 🔒 Private Scripts
If you want to create your own personal scripts, batch files, or workflows without having them tracked by Git, you can place them inside the `my_priv_script/` folder. This directory is included in `.gitignore`, ensuring that any API keys, custom commands, or private channel URLs you store here remain strictly local to your machine.

## 🤖 AI Development Context
This project was primarily developed and is maintained by an AI Agent. To ensure smooth iterations, continuous development, and context-sharing across different AI sessions, this repository utilizes standard AI-handoff documents:

- **`PROJECT_CONTEXT.md`**: Provides the AI with the overarching business logic, project constraints, directory structures, and strict coding conventions. **When developing new features, the AI must read this first.**
- **`HANDOFF.md`**: Acts as a state-saving document. It records the progress of the current session, completed features, known unresolved bugs, and the next steps. **The AI updates this at the end of its session and reads it at the beginning of the next.**

If you are using another AI assistant to maintain or extend this code, please point the AI to read these two documents before it begins coding.
