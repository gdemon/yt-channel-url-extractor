@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
echo Running test for run_pipeline_url.py with a specific video
python run_pipeline_url.py "https://www.youtube.com/watch?v=KzndAUJQZgI"
