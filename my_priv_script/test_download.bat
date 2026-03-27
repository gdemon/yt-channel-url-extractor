@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
echo Running test for yt-channel-url-extractor with download flag
python main.py "https://www.youtube.com/@YouTube" -d
