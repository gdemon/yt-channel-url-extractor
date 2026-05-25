@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set BROWSER=chrome
if not "%~1"=="" set BROWSER=%~1

echo Running test for yt-channel-url-extractor using browser: %BROWSER%
python main.py "https://www.youtube.com/playlist?list=PLVu0pIxQ7F-ywTXU3Ui5X4AzRdjqdWltm" --cookies-from-browser %BROWSER%

pause
