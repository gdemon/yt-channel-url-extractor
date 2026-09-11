@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
echo Running test for output directory support
python scripts\test\test_output_dir.py
pause
