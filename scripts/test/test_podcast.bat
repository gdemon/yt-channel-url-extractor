@echo off
call "%~dp0..\..\venv\Scripts\activate.bat"
echo Running test for Podcast RSS Fetch
python "%~dp0..\..\fetch_podcast.py" "https://feeds.soundon.fm/podcasts/91be014b-9f55-4bf3-a910-b232eda82d11.xml"
