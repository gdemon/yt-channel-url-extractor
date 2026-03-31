import os
# Suppress huggingface_hub symlink warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import requests
import xml.etree.ElementTree as ET
import subprocess
import logging
from datetime import datetime, date
from pathlib import Path
from email.utils import parsedate_to_datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Base directory for storing stuff
BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR / "result" / "podcasts"

# Default Whisper CLI Command
# 您可以在這裡替換成您實際打進終端機的 Whisper 指令。
# {audio_file} 與 {output_dir} 是腳本預留的自動替換標籤。
WHISPER_CMD_TEMPLATE = [
    "whisper",
    "{audio_file}",
    "--model", "medium",  # if large-v3 requires too much memory, adjust accordingly
    "--language", "zh",
    "--device", "cuda",
    "--output_dir", "{output_dir}"
]

def fetch_latest_podcast(rss_url: str, target_date: date = None):
    if target_date is None:
        target_date = date.today()
        
    logging.info(f"Fetching RSS feed from: {rss_url}")
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch RSS feed: {e}")
        return
    
    # Parse XML
    try:
        root = ET.fromstring(response.content)
    except Exception as e:
        logging.error(f"Failed to parse RSS XML: {e}")
        return
        
    channel = root.find("channel")
    if channel is None:
        logging.error("Invalid RSS format: no <channel> tag found.")
        return
        
    logging.info(f"Checking episodes for date: {target_date}")
    
    for item in channel.findall("item"):
        title_tag = item.find("title")
        pub_date_tag = item.find("pubDate")
        enclosure_tag = item.find("enclosure")
        
        if title_tag is None or pub_date_tag is None or enclosure_tag is None:
            continue
            
        title = title_tag.text.strip()
        pub_date_str = pub_date_tag.text.strip()
        mp3_url = enclosure_tag.attrib.get("url")
        
        if not mp3_url:
            continue
            
        # Parse publication date (RFC-822 format typical for RSS)
        try:
            dt = parsedate_to_datetime(pub_date_str)
            item_date = dt.date()
        except Exception as e:
            logging.warning(f"Failed to parse date '{pub_date_str}': {e}")
            continue
            
        if item_date == target_date:
            logging.info(f"Found matching episode: {title}")
            _process_episode(title, item_date, mp3_url)
            return  # Stop after finding the latest target day episode
            
    logging.info(f"No episode found for {target_date}.")

def _process_episode(title: str, item_date: date, mp3_url: str):
    # Sanitize title for filesystem (remove Windows invalid chars)
    safe_title = "".join([c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title])
    
    # Create folder: e.g., result/podcasts/2026-03-31_EP1068
    folder_name = f"{item_date.isoformat()}_{safe_title}"
    output_dir = RESULT_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mp3_path = output_dir / "audio.mp3"
    
    if not mp3_path.exists():
        logging.info(f"Downloading MP3 to {mp3_path} ...")
        try:
            _download_file(mp3_url, mp3_path)
        except Exception as e:
            logging.error(f"Failed to download MP3: {e}")
            return
    else:
        logging.info(f"MP3 already exists at {mp3_path}, skipping download.")
        
    # Check if transcript already exists
    srt_path = output_dir / "audio.srt"
    txt_path = output_dir / "audio.txt"
    if srt_path.exists() or txt_path.exists():
        logging.info(f"Transcription already exists in {output_dir}, skipping Whisper.")
        return
        
    # Run Whisper
    logging.info("Starting local Whisper transcription...")
    
    cmd = []
    for arg in WHISPER_CMD_TEMPLATE:
        if arg == "{audio_file}":
            cmd.append(str(mp3_path))
        elif arg == "{output_dir}":
            cmd.append(str(output_dir))
        else:
            cmd.append(arg)
            
    logging.info(f"Command: {' '.join(cmd)}")
    try:
        # Run process
        subprocess.run(cmd, check=True)
        logging.info("Transcription completed successfully.")
    except FileNotFoundError:
        logging.error("Failed: 'whisper' command could not be found.")
        logging.warning("Please ensure 'whisper' CLI is available in your PATH or update WHISPER_CMD_TEMPLATE explicitly.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Whisper subprocess failed with exit code: {e.returncode}")
    except Exception as e:
        logging.error(f"Exception while running Whisper CLI: {e}")

def _download_file(url: str, dest_path: Path):
    with requests.get(url, stream=True, timeout=20) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch and transcribe the latest podcast episode from an RSS feed.")
    parser.add_argument("url", type=str, help="Target podcast RSS URL.")
    parser.add_argument("--date", type=str, help="Target date in YYYY-MM-DD format (default: today).")
    args = parser.parse_args()
    
    target_dt = None
    if args.date:
        try:
            target_dt = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logging.error("Invalid date format. Please use YYYY-MM-DD (e.g., 2026-03-31).")
            exit(1)
            
    fetch_latest_podcast(args.url, target_date=target_dt)
