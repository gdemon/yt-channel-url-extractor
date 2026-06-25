@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
echo Running test for run_pipeline_api.py with @YouTube channel
python run_pipeline_api.py "https://www.youtube.com/@YouTube"
