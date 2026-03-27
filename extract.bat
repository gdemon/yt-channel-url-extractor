@echo off
cd /d "%~dp0"

set CHANNEL_URL=https://www.youtube.com/playlist?list=PLVu0pIxQ7F-yvxR_dCP_zBgChK3s84b99

echo Checking YouTube URL: %CHANNEL_URL%
echo.

call venv\Scripts\activate.bat
python main.py "%CHANNEL_URL%" %*

echo.
echo Finished exploring URL.
pause
